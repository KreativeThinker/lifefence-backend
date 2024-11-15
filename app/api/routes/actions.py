from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

from app.models import Action, Action_Pydantic
from app.models.location import Location
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/actions", tags=["actions"])


class CreateAction(BaseModel):
    trigger_function: str
    location_id: int
    start_time: datetime
    end_time: datetime


# Route to create a new action
@router.post("/new", response_model=Action_Pydantic)
async def create_action(
    action: CreateAction,
    current_user: User = Depends(get_current_user),
):
    __import__("pprint").pprint(action.model_dump_json())
    try:
        location = await Location.get(id=action.location_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Location not found")

    new_action = await Action.create(
        trigger_function=action.trigger_function,
        location=location,
        user=current_user,
        start_time=action.start_time,
        end_time=action.end_time,
    )
    print(new_action.end_time)
    return await Action_Pydantic.from_tortoise_orm(new_action)


@router.get("/view", response_model=List[Action_Pydantic])
async def view_actions(
    location_id: int, current_user: User = Depends(get_current_user)
):
    current_time = datetime.now()

    actions = await Action.filter(
        user=current_user,
        location__id=location_id,
        start_time__lte=current_time,
        end_time__gte=current_time,
        used=False,
    )

    return actions


# Route to trigger a task
@router.get("/trigger/{trigger}")
async def trigger_action(trigger: int, current_user: User = Depends(get_current_user)):
    current_time = datetime.now()
    action = await Action.get_or_none(
        user=current_user,
        id=trigger,
        start_time__lte=current_time,
        end_time__gte=current_time,
        used=False,
    )

    if not action:
        raise HTTPException(status_code=404, detail="Trigger not found or already used")

    # Set action as used
    action.used = True
    await action.save()

    # Execute the trigger (placeholder logic, add actual logic here)
    return {
        "message": action.trigger_function,
        "action": await Action_Pydantic.from_tortoise_orm(action),
    }

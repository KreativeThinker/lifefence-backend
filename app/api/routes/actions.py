from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from models import Action, Action_Pydantic
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_queryset_creator
from tortoise.exceptions import DoesNotExist

from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/actions", tags=["actions"])


class ActionCreate(BaseModel):
    trigger_function: str
    user: User
    start_time: datetime
    end_time: datetime


@router.post("/new", response_model=Action_Pydantic)
async def create_action(
    action: ActionCreate, current_user: User = Depends(get_current_user)
):
    new_action = await Action.create(
        trigger_function=action.trigger_function,
        user=current_user.id,
        start_time=action.start_time,
        end_time=action.end_time,
    )
    return await Action_Pydantic.from_tortoise_orm(new_action)


@router.get("/view", response_model=List[Action_Pydantic])
async def get_actions_by_time(
    start: datetime,
    end: datetime,
    location: ,
    current_user: User = Depends(get_current_user),
):
    actions = await Action.filter(
        user_id=current_user.id,
        start_time__gte=start,
        end_time__lte=end,
        location=location,
    )
    return await pydantic_queryset_creator(Action).from_queryset(actions)


@router.get("/trigger/{trigger_function}", response_model=Action_Pydantic)
async def trigger_action(
    trigger_function: str, current_user: User = Depends(get_current_user)
):
    try:
        action = await Action.get(
            trigger_function=trigger_function, user_id=current_user.id
        )
        result = await execute_trigger_function(action)
        return result
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Action not found")


async def execute_trigger_function(action: Action):
    # Update the `executed` field to True
    await action.update_from_dict({"executed": True})
    await action.save()
    return {"status": "Function triggered", "function": action.trigger_function}

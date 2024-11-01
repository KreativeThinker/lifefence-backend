from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.routes.auth import get_current_user
from app.models.location import Location
from app.models.task import Task, Task_Pydantic
from app.models.user import User

router = APIRouter(prefix="/task", tags=["task"])


class TaskCreate(BaseModel):
    title: str
    start_date: datetime
    due_date: datetime
    location_id: Optional[int] = None
    parent_task_id: Optional[int] = None

    class Config:
        from_attributes = True


router = APIRouter(prefix="/task", tags=["task"])


@router.post("/new", response_model=Task_Pydantic)
async def create_task(
    task_data: TaskCreate, current_user: User = Depends(get_current_user)
):
    location = None
    if task_data.location_id:
        location = await Location.get_or_none(
            id=task_data.location_id, user=current_user
        )
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

    parent_task = None
    if task_data.parent_task_id:
        parent_task = await Task.get_or_none(
            id=task_data.parent_task_id, user=current_user
        )
        if not parent_task:
            raise HTTPException(status_code=404, detail="Parent task not found")

    task = await Task.create(
        title=task_data.title,
        start_date=task_data.start_date,
        due_date=task_data.due_date,
        location=location,
        parent_task=parent_task,
        user=current_user,
    )
    return await Task_Pydantic.from_tortoise_orm(task)


@router.get("/view/location")
async def get_task_by_location(
    location_id: int, current_user: User = Depends(get_current_user)
):

    tasks = await Task.filter(location__id=location_id, user=current_user).all()
    return [await Task_Pydantic.from_tortoise_orm(task) for task in tasks]


@router.get("/view/{task_id}/subtask")
async def get_subtasks(task_id: int, current_user: User = Depends(get_current_user)):
    subtasks = await Task.filter(user=current_user, parent_task=task_id)
    return subtasks


@router.get("/view/{task_id}")
async def get_task_by_id(task_id: int, current_user: User = Depends(get_current_user)):
    task = await Task.get_or_none(id=task_id, user=current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await Task_Pydantic.from_tortoise_orm(task)


@router.get("/view")
async def get_tasks(current_user: User = Depends(get_current_user)):
    tasks = await Task.filter(user=current_user).all()
    return [await Task_Pydantic.from_tortoise_orm(task) for task in tasks]


@router.post("/complete/{task_id}", response_model=Task_Pydantic)
async def complete_task(task_id: int, current_user: User = Depends(get_current_user)):
    task = await Task.get_or_none(id=task_id, user=current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    await task.save()
    return await Task_Pydantic.from_tortoise_orm(task)

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from tortoise.expressions import Q

from app.models import Group, GroupTask_Pydantic, User
from app.models.group_task import GroupTask
from app.utils.auth import get_current_user

router = APIRouter(prefix="/group-tasks", tags=["group-tasks"])


# Request Models
class GroupTaskCreate(BaseModel):
    group_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class GroupTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


# Helper function to check group membership
async def verify_group_member(group_id: int, user_id: int) -> bool:
    group = await Group.get_or_none(id=group_id)
    if not group:
        return False
    return await group.members.filter(id=user_id).exists()


# Routes
@router.post("/new", response_model=GroupTask_Pydantic)
async def create_group_task(
    task: GroupTaskCreate, current_user: User = Depends(get_current_user)
):
    """Create a new group task"""
    if not await verify_group_member(task.group_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")

    # Verify assigned user is in the group if provided
    if task.assigned_to_id and not await verify_group_member(
        task.group_id, task.assigned_to_id
    ):
        raise HTTPException(
            status_code=400, detail="Assigned user is not a member of this group"
        )

    task_obj = await GroupTask.create(
        group_id=task.group_id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        assigned_to_id=task.assigned_to_id,
        created_by=current_user,
    )
    return await GroupTask_Pydantic.from_tortoise_orm(task_obj)


@router.get("/view/{group_id}", response_model=List[GroupTask_Pydantic])
async def get_group_tasks(
    group_id: int,
    current_user: User = Depends(get_current_user),
    completed: Optional[bool] = None,
):
    """Get all tasks for a specific group"""
    if not await verify_group_member(group_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")

    query = Q(group_id=group_id)
    if completed is not None:
        query &= Q(completed=completed)

    tasks = await GroupTask.filter(query).order_by("-created_at")
    return [await GroupTask_Pydantic.from_tortoise_orm(task) for task in tasks]


@router.get("/assigned", response_model=List[GroupTask_Pydantic])
async def get_assigned_tasks(
    current_user: User = Depends(get_current_user), completed: Optional[bool] = None
):
    """Get all tasks assigned to the current user"""
    query = Q(assigned_to_id=current_user.id)
    if completed is not None:
        query &= Q(completed=completed)

    tasks = await GroupTask.filter(query).order_by("-created_at")
    return [await GroupTask_Pydantic.from_tortoise_orm(task) for task in tasks]


@router.get("/{task_id}", response_model=GroupTask_Pydantic)
async def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    """Get a specific task by ID"""
    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not await verify_group_member(task.group, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")

    return await GroupTask_Pydantic.from_tortoise_orm(task)


@router.patch("/{task_id}", response_model=GroupTask_Pydantic)
async def update_task(
    task_id: int,
    task_update: GroupTaskUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a task"""
    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not await verify_group_member(task.group, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")

    # Verify assigned user is in the group if provided
    if task_update.assigned_to_id and not await verify_group_member(
        task.group, task_update.assigned_to_id
    ):
        raise HTTPException(
            status_code=400, detail="Assigned user is not a member of this group"
        )

    update_data = task_update.model_dump(exclude_unset=True)
    await task.update_from_dict(update_data).save()
    return await GroupTask_Pydantic.from_tortoise_orm(task)


@router.post("/{task_id}/toggle", response_model=GroupTask_Pydantic)
async def toggle_task_completion(
    task_id: int, current_user: User = Depends(get_current_user)
):
    """Toggle task completion status"""
    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not await verify_group_member(task.group, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")

    task.completed = not task.completed
    await task.save()
    return await GroupTask_Pydantic.from_tortoise_orm(task)


@router.post("/{task_id}/assign/{user_id}", response_model=GroupTask_Pydantic)
async def assign_task(
    task_id: int, user_id: int, current_user: User = Depends(get_current_user)
):
    """Assign a task to a specific user"""
    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not await verify_group_member(task.group, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")

    if not await verify_group_member(task.group, user_id):
        raise HTTPException(
            status_code=400, detail="Assigned user is not a member of this group"
        )

    task.assigned_to_id = user_id
    await task.save()
    return await GroupTask_Pydantic.from_tortoise_orm(task)


@router.delete("/{task_id}")
async def delete_task(task_id: int, current_user: User = Depends(get_current_user)):
    """Delete a task"""
    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not await verify_group_member(task.group, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")

    if task.created_by != current_user:
        raise HTTPException(
            status_code=403, detail="Only task creator can delete the task"
        )

    await task.delete()
    return {"message": "Task deleted successfully"}

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.group import (
    Group,
    GroupMembership,
    GroupTask,
    TaskStatus,
    MembershipRole,
    GroupTask_Pydantic
)
from app.models.location import Location
from app.models.task import Task, Task_Pydantic
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/task", tags=["task"])

# Request Models
class PersonalTaskCreate(BaseModel):
    title: str
    start_date: datetime
    due_date: datetime
    location_id: Optional[int] = None
    parent_task_id: Optional[int] = None

    class Config:
        from_attributes = True

class GroupTaskCreate(BaseModel):
    group_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None
    status: Optional[TaskStatus] = None

class TaskAssign(BaseModel):
    assigned_to_id: int

# Helper Functions
async def is_task_member(user: User, task_id: int) -> bool:
    """Check if user is a member of the task's group"""
    task = await GroupTask.get_or_none(id=task_id).prefetch_related('group')
    if not task:
        return False
    return await GroupMembership.exists(group=task.group, user=user)

async def can_manage_task(user: User, task_id: int) -> bool:
    """Check if user can manage the task (admin or task creator)"""
    task = await GroupTask.get_or_none(id=task_id).prefetch_related('group')
    if not task:
        return False
    
    membership = await GroupMembership.get_or_none(group=task.group, user=user)
    if not membership:
        return False
    
    return (
        membership.role == MembershipRole.ADMIN
        or task.created_by_id == user.id
        or task.assigned_to_id == user.id
    )

# Personal Task Routes
@router.post("/personal/new", response_model=Task_Pydantic)
async def create_personal_task(
    task_data: PersonalTaskCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new personal task"""
    location = None
    if task_data.location_id:
        location = await Location.get_or_none(
            id=task_data.location_id,
            user=current_user
        )
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

    parent_task = None
    if task_data.parent_task_id:
        parent_task = await Task.get_or_none(
            id=task_data.parent_task_id,
            user=current_user
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

@router.get("/personal/view/location")
async def get_personal_tasks_by_location(
    location_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get personal tasks by location"""
    tasks = await Task.filter(location__id=location_id, user=current_user).all()
    return [await Task_Pydantic.from_tortoise_orm(task) for task in tasks]

@router.get("/personal/view/{task_id}/subtask")
async def get_personal_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get subtasks of a personal task"""
    subtasks = await Task.filter(user=current_user, parent_task=task_id)
    return subtasks

@router.get("/personal/view/{task_id}")
async def get_personal_task_by_id(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get personal task by ID"""
    task = await Task.get_or_none(id=task_id, user=current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await Task_Pydantic.from_tortoise_orm(task)

@router.get("/personal/view")
async def get_personal_tasks(
    current_user: User = Depends(get_current_user)
):
    """Get all personal tasks"""
    tasks = await Task.filter(user=current_user).all()
    return [await Task_Pydantic.from_tortoise_orm(task) for task in tasks]

@router.post("/personal/complete/{task_id}", response_model=Task_Pydantic)
async def complete_personal_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """Mark personal task as complete"""
    task = await Task.get_or_none(id=task_id, user=current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = True
    await task.save()
    return await Task_Pydantic.from_tortoise_orm(task)

# Group Task Routes
@router.post("/group", response_model=GroupTask_Pydantic)
async def create_group_task(
    task_data: GroupTaskCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new group task"""
    membership = await GroupMembership.get_or_none(
        group_id=task_data.group_id,
        user=current_user
    )
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this group"
        )

    if task_data.assigned_to_id:
        assignee_membership = await GroupMembership.exists(
            group_id=task_data.group_id,
            user_id=task_data.assigned_to_id
        )
        if not assignee_membership:
            raise HTTPException(
                status_code=400,
                detail="Assigned user is not a member of this group"
            )

    task = await GroupTask.create(
        group_id=task_data.group_id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        assigned_to_id=task_data.assigned_to_id,
        created_by=current_user
    )

    return await GroupTask_Pydantic.from_tortoise_orm(task)

@router.get("/group", response_model=List[GroupTask_Pydantic])
async def list_group_tasks(
    group_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    assigned_to_me: Optional[bool] = None,
    created_by_me: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """List group tasks with optional filters"""
    query = GroupTask.all()

    if group_id:
        if not await GroupMembership.exists(group_id=group_id, user=current_user):
            raise HTTPException(
                status_code=403,
                detail="You are not a member of this group"
            )
        query = query.filter(group_id=group_id)
    else:
        user_groups = await GroupMembership.filter(user=current_user).values_list('group_id', flat=True)
        query = query.filter(group_id__in=user_groups)

    if status:
        query = query.filter(status=status)
    
    if assigned_to_me:
        query = query.filter(assigned_to=current_user)
    
    if created_by_me:
        query = query.filter(created_by=current_user)

    tasks = await GroupTask_Pydantic.from_queryset(
        query.order_by("-created_at")
    )
    return tasks

@router.get("/group/{task_id}", response_model=GroupTask_Pydantic)
async def get_group_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get group task details"""
    if not await is_task_member(current_user, task_id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )

    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return await GroupTask_Pydantic.from_tortoise_orm(task)

@router.put("/group/{task_id}", response_model=GroupTask_Pydantic)
async def update_group_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update group task details"""
    if not await can_manage_task(current_user, task_id):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this task"
        )

    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if task_data.assigned_to_id:
        assignee_membership = await GroupMembership.exists(
            group_id=task.group_id,
            user_id=task_data.assigned_to_id
        )
        if not assignee_membership:
            raise HTTPException(
                status_code=400,
                detail="Assigned user is not a member of this group"
            )

    update_data = task_data.model_dump(exclude_unset=True)
    if update_data:
        await task.update_from_dict(update_data).save()

    return await GroupTask_Pydantic.from_tortoise_orm(task)

@router.put("/group/{task_id}/status")
async def update_group_task_status(
    task_id: int,
    status: TaskStatus,
    current_user: User = Depends(get_current_user)
):
    """Update group task status"""
    if not await is_task_member(current_user, task_id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task"
        )

    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if (
        task.assigned_to_id != current_user.id
        and not await can_manage_task(current_user, task_id)
    ):
        raise HTTPException(
            status_code=403,
            detail="Only assigned user or admin can update task status"
        )

    task.status = status
    await task.save()

    return await GroupTask_Pydantic.from_tortoise_orm(task)

@router.delete("/group/{task_id}")
async def delete_group_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a group task"""
    if not await can_manage_task(current_user, task_id):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this task"
        )

    task = await GroupTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    await task.delete()
    return {"message": "Task deleted successfully"}
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models import (
    Group,
    Group_Pydantic,
    GroupMembership,
    GroupMembership_Pydantic,
    MembershipRole,
    User,
)
from app.utils.auth import get_current_user


# Updated Response Models
class UserInfo(BaseModel):
    id: int
    username: str
    name: str


class MemberInfo(BaseModel):
    id: int
    user_id: int
    role: str
    joined_at: datetime
    invited_by_id: Optional[int]
    # Add user details
    user_name: str
    user_username: str


class GroupWithMembers(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    members: List[MemberInfo]


router = APIRouter(prefix="/group", tags=["group"])


# Request Models
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class MemberAdd(BaseModel):
    user_id: int
    role: MembershipRole = MembershipRole.MEMBER


# Helper function to check admin status
async def is_group_admin(user: User, group_id: int) -> bool:
    return await GroupMembership.exists(
        group_id=group_id, user_id=user.id, role=MembershipRole.ADMIN
    )


@router.get("/{group_id}/is_admin")
async def check_is_admin(group_id: int, user: User = Depends(get_current_user)) -> bool:
    return await is_group_admin(user, group_id)


# Routes
@router.post("/create", response_model=Group_Pydantic)
async def create_group(
    group_data: GroupCreate, current_user: User = Depends(get_current_user)
):
    """Create a new group and add creator as admin"""
    group = await Group.create(
        name=group_data.name,
        description=group_data.description,
    )

    # Add creator as admin
    await GroupMembership.create(
        group=group, user=current_user, role=MembershipRole.ADMIN
    )

    return await Group_Pydantic.from_tortoise_orm(group)


@router.get("/list", response_model=List[Group_Pydantic])
async def list_user_groups(current_user: User = Depends(get_current_user)):
    """List all groups user is a member of"""
    groups = await Group_Pydantic.from_queryset(
        Group.filter(members=current_user).order_by("-created_at")
    )
    return groups


@router.get("/admin", response_model=List[Group_Pydantic])
async def list_admin_groups(current_user: User = Depends(get_current_user)):
    """List groups where user is admin"""
    groups = await Group_Pydantic.from_queryset(
        Group.filter(
            memberships__user=current_user, memberships__role=MembershipRole.ADMIN
        ).order_by("-created_at")
    )
    return groups


@router.get("/{group_id}", response_model=GroupWithMembers)
async def get_group_details(
    group_id: int, current_user: User = Depends(get_current_user)
):
    """Get detailed group information including members"""
    # Check if user is member of the group
    membership = await GroupMembership.exists(group_id=group_id, user=current_user)
    if not membership:
        raise HTTPException(
            status_code=403, detail="You are not a member of this group"
        )

    # Get group with all necessary related data
    group = await Group.get_or_none(id=group_id).prefetch_related("memberships__user")
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get memberships data with user information
    memberships = (
        await GroupMembership.filter(group_id=group_id)
        .prefetch_related("user")
        .values(
            "id",
            "user_id",
            "role",
            "joined_at",
            "invited_by_id",
            user_name="user__name",
            user_username="user__username",
        )
    )

    # Get group data and explicitly include created_by
    group_data = {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_at": group.created_at,
        "updated_at": group.updated_at,
        "members": [MemberInfo(**membership) for membership in memberships],
    }

    return GroupWithMembers(**group_data)


@router.post("/{group_id}/member", response_model=GroupMembership_Pydantic)
async def add_member(
    group_id: int,
    member_data: MemberAdd,
    current_user: User = Depends(get_current_user),
):
    """Add a new member to the group"""
    # Check if user is admin
    if not await is_group_admin(current_user, group_id):
        raise HTTPException(status_code=403, detail="Only admins can add members")

    # Check if user exists
    new_member = await User.get_or_none(id=member_data.user_id)
    if not new_member:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is already a member
    existing_membership = await GroupMembership.get_or_none(
        group_id=group_id, user_id=member_data.user_id
    )
    if existing_membership:
        raise HTTPException(
            status_code=400, detail="User is already a member of this group"
        )

    # Add member
    membership = await GroupMembership.create(
        group_id=group_id,
        user=new_member,
        role=member_data.role,
        invited_by=current_user,
    )

    return await GroupMembership_Pydantic.from_tortoise_orm(membership)


@router.delete("/{group_id}/member/{user_id}")
async def remove_member(
    group_id: int, user_id: int, current_user: User = Depends(get_current_user)
):
    """Remove a member from the group"""
    # Check if user is admin
    if not await is_group_admin(current_user, group_id):
        raise HTTPException(status_code=403, detail="Only admins can remove members")

    # Cannot remove the last admin
    if user_id == current_user.id:
        admin_count = await GroupMembership.filter(
            group_id=group_id, role=MembershipRole.ADMIN
        ).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last admin")

    # Remove member
    deleted_count = await GroupMembership.filter(
        group_id=group_id, user_id=user_id
    ).delete()

    if not deleted_count:
        raise HTTPException(status_code=404, detail="Member not found in group")

    return {"message": "Member removed successfully"}


@router.put("/{group_id}", response_model=Group_Pydantic)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update group details"""
    # Check if user is admin
    if not await is_group_admin(current_user, group_id):
        raise HTTPException(
            status_code=403, detail="Only admins can update group details"
        )

    group = await Group.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    update_data = group_data.model_dump(exclude_unset=True)
    if update_data:
        await group.update_from_dict(update_data).save()

    return await Group_Pydantic.from_tortoise_orm(group)


@router.delete("/{group_id}")
async def delete_group(group_id: int, current_user: User = Depends(get_current_user)):
    """Delete a group"""
    # Check if user is admin
    if not await is_group_admin(current_user, group_id):
        raise HTTPException(status_code=403, detail="Only admins can delete the group")

    group = await Group.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Delete all memberships and the group
    await GroupMembership.filter(group_id=group_id).delete()
    await group.delete()

    return {"message": "Group deleted successfully"}

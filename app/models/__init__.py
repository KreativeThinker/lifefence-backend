import typing

import tortoise

from app.models.group import (
    Group,
    Group_Pydantic,
    GroupMembership,
    GroupMembership_Pydantic,
    MembershipRole,
)
from app.models.location import (
    Blacklist,
    Blacklist_Pydantic,
    Location,
    Location_Pydantic,
    Office,
    Residence,
)
from app.models.task import Task, Task_Pydantic
from app.models.user import User, User_Pydantic

__all__ = (
    "Blacklist",
    "Blacklist_Pydantic",
    "Location",
    "Location_Pydantic",
    "Office",
    "Residence",
    "Task",
    "Task_Pydantic",
    "User",
    "User_Pydantic",
    "Group",
    "Group_Pydantic",
    "GroupMembership",
    "GroupMembership_Pydantic",
    "MembershipRole",
)


def get_annotations(cls, method=None):
    return typing.get_type_hints(method or cls)


tortoise.contrib.pydantic.utils.get_annotations = get_annotations  # type: ignore[unused-ignore]
tortoise.contrib.pydantic.creator.get_annotations = get_annotations  # type: ignore[unused-ignore]

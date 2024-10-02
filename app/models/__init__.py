import typing

import tortoise
from tortoise.contrib.pydantic.creator import pydantic_model_creator

from app.models.group import Group
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
    "Group",
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
)


def get_annotations(cls, method=None):
    return typing.get_type_hints(method or cls)


tortoise.contrib.pydantic.utils.get_annotations = get_annotations  # type: ignore[unused-ignore]
tortoise.contrib.pydantic.creator.get_annotations = get_annotations  # type: ignore[unused-ignore]

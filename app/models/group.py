from enum import Enum

from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class MembershipRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class Group(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_by = fields.ForeignKeyField("models.User", related_name="created_groups")

    # These will be accessed through GroupMembership
    members = fields.ManyToManyField(
        "models.User",
        through="groupmembership",
        related_name="groups",
        through_fields=("group", "user"),
    )


class GroupMembership(Model):
    id = fields.IntField(pk=True)
    group = fields.ForeignKeyField("models.Group", related_name="memberships")
    user = fields.ForeignKeyField("models.User", related_name="group_memberships")
    role = fields.CharEnumField(MembershipRole, default=MembershipRole.MEMBER)
    joined_at = fields.DatetimeField(auto_now_add=True)
    invited_by = fields.ForeignKeyField(
        "models.User", related_name="group_invites_sent", null=True
    )

    class Meta:
        unique_together = (("group", "user"),)


# Modify Task model to include group field
class TaskUpdate(Model):
    id = fields.IntField(pk=True)
    group = fields.ForeignKeyField(
        "models.Group", related_name="group_tasks", null=True
    )


Group_Pydantic = pydantic_model_creator(Group, name="Group")
GroupMembership_Pydantic = pydantic_model_creator(
    GroupMembership, name="GroupMembership"
)

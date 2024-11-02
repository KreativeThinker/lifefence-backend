from enum import Enum
from datetime import datetime
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class MembershipRole(str, Enum):
    MEMBER = "MEMBER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"

class Group(models.Model):
    """Group model for managing collections of users"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_by = fields.ForeignKeyField('models.User', related_name='created_groups')
    members = fields.ManyToManyField(
        'models.User', through='GroupMembership', related_name='groups'
    )

    class Meta:
        table = "groups"

class GroupMembership(models.Model):
    """Through model for group members with roles"""
    id = fields.IntField(pk=True)
    group = fields.ForeignKeyField('models.Group', related_name='memberships')
    user = fields.ForeignKeyField('models.User', related_name='group_memberships')
    role = fields.CharEnumField(MembershipRole, default=MembershipRole.MEMBER)
    joined_at = fields.DatetimeField(auto_now_add=True)
    invited_by = fields.ForeignKeyField(
        'models.User', null=True, related_name='group_invites_sent'
    )

    class Meta:
        table = "group_memberships"
        unique_together = (("group", "user"),)

class GroupTask(models.Model):
    """Tasks assigned within a group"""
    id = fields.IntField(pk=True)
    group = fields.ForeignKeyField('models.Group', related_name='tasks')
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    due_date = fields.DatetimeField(null=True)
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.PENDING)
    assigned_to = fields.ForeignKeyField(
        'models.User', null=True, related_name='assigned_group_tasks'
    )
    created_by = fields.ForeignKeyField('models.User', related_name='created_group_tasks')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "group_tasks"

class GroupEvent(models.Model):
    """Location-based events for groups"""
    id = fields.IntField(pk=True)
    group = fields.ForeignKeyField('models.Group', related_name='events')
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    location_lat = fields.FloatField()
    location_lng = fields.FloatField()
    trigger_radius_meters = fields.IntField(default=100)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    created_by = fields.ForeignKeyField('models.User', related_name='created_group_events')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "group_events"

# Create Pydantic models
Group_Pydantic = pydantic_model_creator(Group, name="Group")
GroupMembership_Pydantic = pydantic_model_creator(GroupMembership, name="GroupMembership")
GroupTask_Pydantic = pydantic_model_creator(GroupTask, name="GroupTask")
GroupEvent_Pydantic = pydantic_model_creator(GroupEvent, name="GroupEvent")
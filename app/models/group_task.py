from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class GroupTask(models.Model):
    """Tasks assigned within a group"""

    id = fields.IntField(pk=True)
    group = fields.ForeignKeyField("models.Group", related_name="tasks")
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    due_date = fields.DatetimeField(null=True)
    completed = fields.BooleanField(null=False, default=False)
    assigned_to = fields.ForeignKeyField(
        "models.User", null=True, related_name="assigned_group_tasks"
    )
    created_by = fields.ForeignKeyField(
        "models.User", related_name="created_group_tasks"
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class GroupEvent(models.Model):
    """Location-based events for groups"""

    id = fields.IntField(pk=True)
    group = fields.ForeignKeyField("models.Group", related_name="events")
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    location_lat = fields.FloatField()
    location_lng = fields.FloatField()
    trigger_radius_meters = fields.IntField(default=100)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    created_by = fields.ForeignKeyField(
        "models.User", related_name="created_group_events"
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


GroupTask_Pydantic = pydantic_model_creator(GroupTask)
GroupEvent_Pydantic = pydantic_model_creator(GroupEvent)

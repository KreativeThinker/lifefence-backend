from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Action(Model):
    id = fields.IntField(pk=True)
    trigger_function = fields.CharField(max_length=128)
    location = fields.ForeignKeyField(
        "models.Location", related_name="trigger_location"
    )
    start_time = fields.DatetimeField(auto_now_add=True, null=True)
    end_time = fields.DatetimeField(auto_now=True, null=True)
    user = fields.ForeignKeyField("models.User", related_name="user_action")
    used = fields.BooleanField(default=False)


Action_Pydantic = pydantic_model_creator(Action, name="Group")

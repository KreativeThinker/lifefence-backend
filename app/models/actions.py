from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Action(Model):
    id = fields.IntField(pk=True)
    trigger_function = fields.CharField(max_length=128)
    location = fields.ForeignKeyField(
        "models.Location", related_name="trigger_location"
    )
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    user = fields.ForeignKeyField("models.User", related_name="user_action")
    used = fields.BooleanField(default=False)


Action_Pydantic = pydantic_model_creator(Action)

from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Task(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=128)
    start_date = fields.DatetimeField()
    due_date = fields.DatetimeField()
    completed = fields.BooleanField(default=False)
    parent_task = fields.ForeignKeyField(
        "models.Task", related_name="subtask", null=True
    )
    location = fields.ForeignKeyField(
        "models.Location", related_name="task_location", null=True
    )
    user = fields.ForeignKeyField("models.User", related_name="user_task")


Task_Pydantic = pydantic_model_creator(Task)

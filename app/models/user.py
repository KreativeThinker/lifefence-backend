from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128)
    username = fields.CharField(max_length=64, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    dob = fields.DateField()
    # residential_address = fields.ForeignKeyField( "models.Location", related_name="residential_address", null=True)
    # office_address = fields.ForeignKeyField( "models.Location", related_name="office_address", null=True)
    parent = fields.ForeignKeyField("models.User", related_name="child_user", null=True)


User_Pydantic = pydantic_model_creator(User, name="User", exclude=("password",))

from tortoise import Model, fields

# from app.models.user import User


class Group(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=128)
    # users: fields.ReverseRelation[User]

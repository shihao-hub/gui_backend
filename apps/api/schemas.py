from ninja import ModelSchema

from apps.api.models import User


class UserModelSchema(ModelSchema):
    class Meta:
        model = User
        fields = ("id", "username")

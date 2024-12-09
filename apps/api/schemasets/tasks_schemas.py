import enum

from ninja import Schema, Field


# -------------------------------------------------------------------------------------------------------------------- #
# tasks_views.py
# -------------------------------------------------------------------------------------------------------------------- #
class TasksTimedMessageRequestSchema(Schema):
    class TypeEnum(enum.Enum):
        QQ = enum.auto()
        WECHAT = enum.auto()
        QQ_EMAIL = enum.auto()

    # 2024-12-08：为什么传入 Field 之后，api/docs 的 Schemas 里就有这个 Enum 了？这重名咋办？所以这不是最佳实践？
    type: TypeEnum = Field(TypeEnum.QQ)

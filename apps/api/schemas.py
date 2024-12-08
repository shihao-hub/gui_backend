import enum
from typing import Literal, Optional, List, Dict, Union

from ninja import Schema, UploadedFile, Field
from pydantic import validator, field_validator, root_validator
from pydantic_core.core_schema import ValidationInfo


class SuccessSchema(Schema):
    code: int = 1000
    message: str = ""
    data: Union[str, List, Dict, None] = ""  # 设置为 None 时，api/docs 里面默认值是 "string"？为什么...


class ErrorSchema(Schema):
    code: int = 1001
    message: str = ""
    reason: str = ""
    status: str = "Error"  # "Service Unavailable"
    data: Union[str, List, Dict, None] = ""


generic_success_error_responses = {200: SuccessSchema, 400: ErrorSchema}


# -------------------------------------------------------------------------------------------------------------------- #
# index_views.py
# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# tools_views.py
# -------------------------------------------------------------------------------------------------------------------- #
class ToolsBase64RequestSchema(Schema):
    class ModeEnum(enum.Enum):
        ENCODE = 0
        DECODE = 1

    class ResponseEncodingEnum(enum.Enum):
        UTF8 = "utf-8"

    mode: ModeEnum = Field(ModeEnum.ENCODE)
    text: Optional[str] = None  # Input should be a valid string, if not be set Optional[str]
    file: Optional[UploadedFile] = None
    response_encoding: ResponseEncodingEnum = Field(ResponseEncodingEnum.UTF8)

    def get_pending_text(self) -> str:
        res = self.text
        if res is None:
            res = self.file.read().decode(self.response_encoding.value)
        return res

    @validator("text", always=True)  # 虽然被弃用的，但是还能用，暂且如此吧
    def check_text_or_file(cls, text, values):
        file = values.get("file")
        if text is None and file is None:
            raise ValueError("Either field 'text' or field 'file' must be provided, but not both can be None.")
        return text


class ToolsBase64ResponseSchema(Schema):
    text: str


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


# -------------------------------------------------------------------------------------------------------------------- #
# redis_views.py
# -------------------------------------------------------------------------------------------------------------------- #
class RedisTodoListItemSchema(Schema):
    value: str

# -------------------------------------------------------------------------------------------------------------------- #
# chatgpt_views.py
# -------------------------------------------------------------------------------------------------------------------- #

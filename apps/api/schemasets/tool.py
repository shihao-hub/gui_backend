import enum
from typing import Literal, Optional, List, Dict, Union, Any

from ninja import Schema, Field, UploadedFile
from pydantic import validator, field_validator, root_validator


class Base64Request(Schema):
    class ModeEnum(enum.Enum):
        ENCODE = 0
        DECODE = 1

    class ResponseEncodingEnum(enum.Enum):
        UTF8 = "utf-8"

    mode: ModeEnum = Field(ModeEnum.ENCODE)
    text: Optional[str] = None  # TODO: 为什么 None swagger-ui 会默认 "string"
    file: Optional[UploadedFile] = None  # TODO: 为什么 UploadedFile swagger-ui 也会默认 "string" -> ! None 标记使它非必填
    response_encoding: ResponseEncodingEnum = Field(ResponseEncodingEnum.UTF8)

    def get_pending_text(self) -> str:
        res = self.text
        if res is None:
            res = self.file.read().decode(self.response_encoding.value)
        return res

    @validator("text", always=True)  # TODO: 虽然被弃用的，但是还能用，暂且如此吧
    def check_text_or_file(cls, text, values):
        file = values.get("file")
        if text is None and file is None:
            raise ValueError("Either field 'text' or field 'file' must be provided, but not both can be None.")
        return text


class Base64Response(Schema):
    text: str

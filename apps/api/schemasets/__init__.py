import time
from typing import Literal, Optional, List, Dict, Union, Any

from pydantic import field_validator, root_validator, model_validator

from django.utils import timezone
from ninja import Schema, Field
from ninja.schema import DjangoGetter

from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

log = Log()


class SuccessSchema(Schema):
    """
    {
        "success": True,
        "message": "Books retrieved successfully.",
        "data": [],
        "meta": {
            "requestId": "abc124",
            "timestamp": "2023-10-01T12:35:00Z"
        },
        "errors": null,
    }
    """
    success: bool = True
    message: str = ""
    data: Union[Dict, List, str, int, float, None] = None

    # 可能的附加信息，如分页信息或其他元数据。 -> meta["timestamp"] = timezone.now()
    meta: Optional[Dict] = Field(default_factory=dict)
    errors: None = None

    # @field_validator("meta", mode="after")
    # @knowledge("pydantic field_validator mode=after")
    # def set_meta(cls, value):
    #     # 测试发现，此处不执行...
    #     log.info(value)
    #     if value.get("timestamp") is None:
    #         value["timestamp"] = timezone.now()

    # @root_validator(pre=True)
    # def set_meta(cls, values: "DjangoGetter"):
    #     # 在 meta 字段中添加当前时间戳
    #     log.debug(values)
    #     log.debug(type(values))
    #     log.debug(getattr(values, "meta", {}))  # 不存在 get 方法，被注释了。
    #     meta = getattr(values, "meta", {})
    #     if "timestamp" not in meta:
    #         meta["timestamp"] = timezone.now().isoformat()  # 使用当前时间
    #     values['meta'] = meta  # 'DjangoGetter' object does not support item assignment
    #     return values

    # FIXME: 试图在 response=SuccessSchema 时，返回当时的时间点，但是 DjangoGetter 不允许修改...
    #   而且即便由于 meta 是字典这种可变对象，我修改了它，但是实际上修改的还是类变量！！！
    #   毕竟是 classmethod 方法... 这个主要是校验用的...
    #   django-ninja 返回的时候多半调用的是 Schema 内的 from_orm/json_schema 方法，它们也是 classmethod！！！
    @model_validator(mode="after")  # NOQA
    @classmethod
    def set_meta(cls, schema: "SuccessSchema"):
        # 在 meta 字段中添加当前时间戳
        # log.debug(schema)
        # log.debug(type(schema))
        # meta = getattr(schema, "meta", None)
        # if meta is not None:
        #     meta["timestamp"] = time.time()
        return schema


class ErrorSchema(Schema):
    """
    {
        "success": False,
        "message": "The user with ID 1 was not found.",
        "data": null,
        "meta": {
            "requestId": "abc126",
            "timestamp": "2023-10-01T12:36:00Z"
        },
        "errors": [
            {
                "code": "USER_NOT_FOUND",
                "message": "The user with ID 1 was not found.",
                "details": {
                    "requestedId": 1
                }
            }
        ],
    }
    """
    success: bool = False
    message: str = ""
    data: Union[Dict, List, str, int, float, None] = None

    meta: Optional[Dict] = None  # 可能的附加信息，如分页信息或其他元数据。
    errors: Optional[List[Dict]] = None  # 可能的错误信息，如验证错误等。

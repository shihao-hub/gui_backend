from typing import Any

from ninja import Schema, Field
from ninja.types import DictStrAny


class TodoListItemRequestSchema(Schema):
    content: str


class TodoListItemResponseSchema(Schema):
    unique_id: str = Field(..., alias="_id")
    content: str

    # 使用别名！
    def dict(self, *a: Any, **kw: Any) -> DictStrAny:
        return super().dict(*a, **kw, by_alias=True)

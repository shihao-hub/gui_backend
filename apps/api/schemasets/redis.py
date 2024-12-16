from datetime import datetime
from typing import List

from ninja import Schema, Field


class TodoListItemSchema(Schema):
    # QUESTION:
    #   Schema 准确的使用场景在哪？滥用会导致 Schema 类型过多啊...
    value: str


class TodoListItemV2Schema(Schema):
    # 2024-12-15：第二版本的设定
    id: int = Field()
    title: str
    description: str
    completed: bool = False
    created_at: datetime
    updated_at: datetime
    due_date: datetime
    priority: str
    tags: List[str] = Field(default_factory=lambda: ["default"])
    subtasks: List["TodoListItemV2Schema"] = Field(default_factory=list)  # 递归类型

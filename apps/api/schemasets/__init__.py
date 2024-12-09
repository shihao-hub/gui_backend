from typing import List, Dict, Union
from ninja import Schema

# 2024-12-09：不需要类似 viewsets 目录一样全部导入，用到的时候导入就行了
# from apps.api.schemasets import async_schemas
# from apps.api.schemasets import chatgpt_schemas
# from apps.api.schemasets import index_schemas
# from apps.api.schemasets import redis_schemas
# from apps.api.schemasets import tasks_schemas
# from apps.api.schemasets import tools_schemas

class SuccessSchema(Schema):
    code: int = 1000
    message: str = ""
    status: str = "success"
    data: Union[str, List, Dict, None] = ""  # 设置为 None 时，api/docs 里面默认值是 "string"？为什么...


class ErrorSchema(Schema):
    code: int = 1001
    message: str = ""
    reason: str = ""
    status: str = "error"  # "Service Unavailable"
    data: Union[str, List, Dict, None] = ""

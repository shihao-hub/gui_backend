from django.http import HttpRequest, HttpResponse
from ninja import Router

from apps.api.schemas import SuccessSchema, ErrorSchema, TasksTimedMessageRequestSchema
from apps.api.views import api
from apps.api.viewsets.widgets import timed_message

router = Router(tags=["tasks"])
api.add_router("/tasks", router)


# 为什么必须设置 200 和 其他？200 为什么没有默认值？那这样的话我不如封装一个 response 函数呢...
@router.post("/timed_message", response={200: SuccessSchema, 503: ErrorSchema}, summary="定时发送信息")
def timed_message(request: HttpRequest, data: TasksTimedMessageRequestSchema):
    """
        **定时发送信息**
        - QQ
        - 微信
        - 邮箱

        **信息支持格式**
        - 字符
        - 图片

        最好能支持富文本内容
    """

    try:
        return 200, {"message": f"{data}"}
    except Exception as e:
        # log.error(f"{e}\n{traceback.format_exc()}")
        return 503, {"message": "Service Unavailable", "reason": f"{e.__class__}: {e}"}

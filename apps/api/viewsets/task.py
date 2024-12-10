import traceback

from django.http import HttpRequest, HttpResponse
from ninja import Router

from apps.api.exceptions import BadRequestError
from apps.api.schemas import TasksTimedMessageRequestSchema, SuccessSchema
from apps.api.viewsets.widgets import timed_message
from apps.api.shared.singleton import Singleton
from apps.api.shared.utils import generic_response, get_registered_router
from apps.core.shared.log import Log

api = Singleton.api
log = Log()

router = get_registered_router(api, __file__)


# 为什么必须设置 200 和 其他？200 为什么没有默认值？那这样的话我不如封装一个 response 函数呢...
@router.post("/timed_message", response=generic_response, summary="定时发送信息")
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
        return {"message": f"{data}"}
    except Exception as e:
        log.error(f"{e}\n{traceback.format_exc()}")
        raise BadRequestError(f"{e}") from e

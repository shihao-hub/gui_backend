# 2024-12-12：正常用 app 来拆分不同类别的路由的时候，可以将总路由放在 router.py 中，现在不是，ninja api 我全部放在 api app 中了。
# 即：一个 app 一个 router.py，里面有个主路由。但是目前我是存放了 api，因为只用 app api 里面和 ninja 有关

import traceback

import orjson

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from ninja.parser import Parser
from ninja_extra import NinjaExtraAPI

from apps.api.exceptions import ServiceUnavailableError, BadRequestError
from apps.api.routersets.tool import CommentCollectorController
from apps.api.routersets.redis import TodoListController, QuickNoteController
from apps.api.schemasets import ErrorSchema
from apps.core.shared.log import Log

log = Log()


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


api = NinjaExtraAPI(parser=ORJSONParser(), docs_decorator=None)  # staff_member_required -> 访问 API 文档需要登录

api.add_router("/chatgpt", "apps.api.routersets.chatgpt.router")
api.add_router("/exercise", "apps.api.routersets.exercise.router")
api.add_router("/model", "apps.api.routersets.model.router")
api.add_router("/mongodb", "apps.api.routersets.mongodb.router")
api.add_router("/ocr", "apps.api.routersets.ocr.router")
api.add_router("/redis", "apps.api.routersets.redis.router")
api.add_router("/task", "apps.api.routersets.task.router")
api.add_router("/tool", "apps.api.routersets.tool.router")

# TODO: ninja_extra 的如何测试？【必须看一下源码】，找到它的 router 比较重要...
#   题外话，【如何阅读源码呢？】不画图真的很难（因为跳来跳去），但是画什么图呢？类图？【是不是又得学 UML？】
api.register_controllers(
    CommentCollectorController,
    TodoListController,
    QuickNoteController
)


# -------------------------------------------------------------------------------------------------------------------- #
#
# -------------------------------------------------------------------------------------------------------------------- #

# TODO: 定义一个全局响应处理器，修改响应为 200 的情况。肯定可以做到，但是 django-ninja 不知道如何做。


# -------------------------------------------------------------------------------------------------------------------- #
# exceptions
# -------------------------------------------------------------------------------------------------------------------- #
@api.exception_handler(Exception)  # 设置 API 的全局响应类型，捕获所有未处理的异常
def global_exception_handler(request: HttpRequest, exc: Exception):
    log.error(f"{exc}\n{traceback.format_exc()}")
    return api.create_response(
        request,
        ErrorSchema(message=f"{exc.__class__}: {exc}").dict(),
        status=500
    )


@api.exception_handler(ServiceUnavailableError)
def service_unavailable(request: HttpRequest, exc: ServiceUnavailableError):
    return api.create_response(
        request,
        ErrorSchema(message=f"{exc.__class__}: {exc}").dict(),
        status=503
    )


@api.exception_handler(BadRequestError)
def bad_request(request: HttpRequest, exc: BadRequestError):
    # TODO: 此处要打印的信息可以优化
    return api.create_response(
        request,
        ErrorSchema(message=f"{exc.__class__}: {exc}", data=exc.data).dict(),
        status=400
    )

# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# [URL 的反向解析](https://django-ninja.cn/guides/urls/) -> django templates 会用到

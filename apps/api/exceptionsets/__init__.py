import traceback

from django.http import HttpRequest

from apps.api.exceptions import ServiceUnavailableError, BadRequestError
from apps.api.views import api
from apps.api.schemas import ErrorSchema
from apps.core.shared.log import Log

log = Log()


@api.exception_handler(Exception)  # 设置 API 的全局响应类型，捕获所有未处理的异常
def global_exception_handler(request: HttpRequest, exc: Exception):
    log.error(f"{exc}\n{traceback.format_exc()}")
    return api.create_response(
        request,
        ErrorSchema(message=str(exc)).dict(),
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
        ErrorSchema(**dict(
            message=f"{exc.__class__}: {exc}",
            data=exc.data
        )).dict(),
        status=400
    )

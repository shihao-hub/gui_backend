__all__ = ["ServiceUnavailableError", "BadRequestError"]

import traceback

from django.http import HttpRequest

from apps.api.views import api
from apps.api.schemasets import ErrorSchema
from apps.core.shared.log import Log

log = Log()


class ServiceUnavailableError(Exception):
    pass


class BadRequestError(Exception):
    pass


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
        ErrorSchema(message=str(exc)).dict(),
        status=503
    )


@api.exception_handler(BadRequestError)
def bad_request(request: HttpRequest, exc: BadRequestError):
    return api.create_response(
        request,
        ErrorSchema(message=str(exc)).dict(),
        status=400
    )

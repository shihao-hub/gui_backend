"""
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest

from apps.api.settings import redis_db as db
from apps.core.shared.log import Log

log = Log()


class RequestCountMiddleware(MiddlewareMixin):

    @staticmethod
    def get_counter_key(path: str) -> str:
        return "RequestCountMiddleware:" + path

    def process_request(self, request: HttpRequest):
        this = self

        key = self.get_counter_key(request.path)
        val = db.get(key)
        if val is None:
            db.set(key, 1)
        else:
            db.set(key, int(val) + 1)  # the type of val is bytes, so we need to convert it to int
"""

from django.utils.deprecation import MiddlewareMixin

from apps.api.settings import redis_db as db


class RequestCountMiddleware(MiddlewareMixin):
    def process_request(self, request):
        this = self

        # 统计各个请求的请求次数，用 Redis 的 zset 实现
        key = "apps:api:middleware:RequestCountMiddleware"
        path = request.path
        score = db.zscore(key, path)
        if score is None:
            score = 1
        else:
            score += 1
        db.zadd(key, {path: score})

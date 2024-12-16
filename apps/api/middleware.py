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

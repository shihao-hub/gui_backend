import json

import redis

from django.http import HttpRequest
from ninja import Router

from apps.core.shared.log import Log

log = Log()

router = Router(tags=["redis"])

db = redis.StrictRedis(host="localhost", port=6379, db=0)


@router.get("/test", summary="api:redis:test")
def test(request: HttpRequest):
    pass




import asyncio
import time

from ninja import Router
from asgiref.sync import sync_to_async

from django.http import HttpRequest

from apps.api.shared.singleton import Singleton
from apps.core.shared.log import Log

api = Singleton.api
log = Log()

router = Router(tags=["async"])
api.add_router("/async", router)


@router.get("/say-sync")
def say_after_sync(request, delay: int, word: str):
    time.sleep(delay)
    return {"saying": word}


@router.get("/say-async")
async def say_after_async(request, delay: int, word: str):
    await asyncio.sleep(delay)
    return {"saying": word}

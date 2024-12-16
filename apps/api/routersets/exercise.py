import asyncio
import time
from typing import List

from asgiref.sync import sync_to_async

from ninja import Router, Query, Schema, Field, ModelSchema

from apps.core.shared.log import Log

log = Log()

router = Router(tags=["exercise"])


# NOTE:
#   ninja_crud 和 ninja_extra 咋总是破坏我的结构！

# TODO: 把 async 用异步服务器运行起来！！！用 python 练习 async，那么学习 js 的异步时应该更好掌握！
@router.get("/say")
def say_after(request, delay: int, word: str):
    time.sleep(delay)
    return {"saying": word}


# 目前，Django 的某些关键部分不能在异步环境中安全操作，因为它们具有全局状态，该状态不是协程感知的。
# 所以 async 用协程实现的！？

# Django 的这些部分被分类为“异步不安全”，并在异步环境中受到保护，不执行。
# 所以，如果你这样做：async def search(request, post_id: int): blog = Blog.objects.get(pk=post_id)
# 它会抛出一个错误。在异步 ORM 实现之前，你可以使用 sync_to_async() 适配器:
# from asgiref.sync import sync_to_async
# async def search(request, post_id: int): blog = await sync_to_async(Blog.objects.get)(pk=post_id)

# 自从 Django version 4.1，Django 带有异步版本的 ORM 操作。
# 这些在大多数情况下消除了使用 sync_to_async的需要。
# 异步操作具有与它们的同步对应操作相同的名称，但前面加上 a。-> blog = await Blog.objects.aget(pk=post_id)

@router.get("/async-say")
async def async_say_after(request, delay: int, word: str):
    await asyncio.sleep(delay)
    return {"saying": word}


class HelloResponse(Schema):
    msg: str


@router.get("/hello", response=HelloResponse)
def hello(request):
    return {"msg": "Hello World"}


class Filters(Schema):
    limit: int = 100
    offset: int = None
    query: str = None
    category__in: List[str] = Field(..., alias="categories")  # 这个别名给前端显示的？api/docs，但是应该不止


@router.get("/filter")
def events(request, filters: Query[Filters]):
    return {"filters": filters.dict()}

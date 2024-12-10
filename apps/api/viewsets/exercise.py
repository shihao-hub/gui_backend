import asyncio
import os.path
import time
from typing import List

from asgiref.sync import sync_to_async
from ninja import Router, Query, Schema, Field, ModelSchema
from ninja.orm.factory import create_schema
from ninja.pagination import paginate, LimitOffsetPagination, PageNumberPagination
from ninja_crud import views, viewsets

from django.http import HttpRequest, HttpResponse

from apps.api.models import Book, User
from apps.api.schemas import BookFilterSchema, SuccessSchema, ErrorSchema
from apps.api.shared.singleton import Singleton
from apps.api.shared.utils import generic_response, get_registered_router
from apps.core.shared.log import Log

api = Singleton.api
log = Log()

router = Router(tags=["exercise"])
api.add_router("/exercise", router)

book_router = Router()
router.add_router("/book", book_router, tags=["exercise"])  # 多级路由/嵌套路由器


# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
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


# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
class HelloResponse(Schema):
    msg: str


@router.get("/hello", response=HelloResponse)
def hello(request):
    return {"msg": "Hello World"}


# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


class UserModelSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ["id", "username"]
        alias_generator = to_camel
        populate_by_name = True  # !!!!!! <--------


# (N)! 分页！（为什么 ninja_extra 和 ninja 的分页函数几乎一模一样）
# LimitOffsetPagination 限制偏移分页 (默认) -> limit, offset
# PageNumberPagination 页码分页 -> page
@router.get("/users", response=List[UserModelSchema], by_alias=True)  # !!!!!! <-------- by_alias
@paginate(PageNumberPagination, page_size=10)
def get_users(request: HttpRequest):
    # (N): 这里的 UserSchema 不需要实例化，解答了为什么我修改 UserModelSchema 的 __init__ 没用！
    # return {"data": [UserModelSchema.from_orm(e) for e in User.objects.all()]}

    # 啊？SuccessSchema 不能这样了，否则分页的时候提示：
    # ninja.errors.ConfigError: "" has no collection response (e.g. response=List[SomeSchema])
    # 这怎么办！这怎么办！这怎么办！这怎么办！这怎么办！这怎么办！
    # https://django-ninja.cn/guides/response/pagination

    return User.objects.all()


# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
class Filters(Schema):
    limit: int = 100
    offset: int = None
    query: str = None
    category__in: List[str] = Field(..., alias="categories")  # 这个别名给前端显示的？api/docs，但是应该不止


@router.get("/filter")
def events(request, filters: Query[Filters]):
    return {"filters": filters.dict()}


class BookViewSet(viewsets.APIViewSet):
    # ninja_crud
    api = book_router
    model = Book

    default_request_body = create_schema(Book, name="BookRequestSchema", exclude=("id",))
    default_response_body = create_schema(Book, name="BookResponseSchema")

    list_departments = views.ListView()
    create_department = views.CreateView()
    read_department = views.ReadView()
    update_department = views.UpdateView()
    delete_department = views.DeleteView()


@router.get("/books2/lists", response=generic_response)
def list_books(request: HttpRequest, filters: BookFilterSchema = Query(...)):
    model_schema = create_schema(Book, name="BookResponseSchema")

    qs = Book.objects.all()
    qs = filters.filter(qs)
    return {"data": [model_schema.from_orm(e) for e in qs]}

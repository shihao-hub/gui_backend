import os.path
from typing import List

from django.http import HttpRequest, HttpResponse

from ninja import Router, Query, Schema, Field, ModelSchema
from ninja.orm.factory import create_schema
from ninja.pagination import paginate, LimitOffsetPagination, PageNumberPagination
from ninja_crud import views, viewsets

from apps.api.models import Book, User
from apps.api.schemas import BookFilterSchema, BookModelSchema
from apps.api.schemasets import SuccessSchema, ErrorSchema
from apps.api.shared.utils import generic_response, get_registered_router
from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

router = Router(tags=["model"])


class BookViewSet(viewsets.APIViewSet):
    # ninja_crud，自动生成 list, create, read, update, delete 接口，分别为 GET, POST, GET, PUT, DELETE
    router = Router(tags=router.tags)
    model = Book

    default_request_body = create_schema(Book, name="BookRequestSchema", exclude=("id",))
    default_response_body = create_schema(Book, name="BookResponseSchema")

    list_departments = views.ListView()
    create_department = views.CreateView()
    read_department = views.ReadView()
    update_department = views.UpdateView()
    delete_department = views.DeleteView()


router.add_router("/book_cbv", BookViewSet.router)


@router.get("/book_fbv/lists", response=List[BookModelSchema])
@paginate()
@knowledge("分页 paginate")
def list_books(request: HttpRequest, filters: BookFilterSchema = Query(...)):
    qs = Book.objects.all()
    qs = filters.filter(qs)

    # model_schema = create_schema(Book, name="BookResponseSchema")
    # {"data": [model_schema.from_orm(e) for e in qs]} -> response=generic_response
    return qs


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

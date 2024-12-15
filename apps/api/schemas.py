import enum
from typing import Literal, Optional, List, Dict, Union, Any

from ninja import Schema, ModelSchema, FilterSchema, Field, UploadedFile
from ninja.types import DictStrAny
from pydantic import validator, field_validator, root_validator

from django.utils import timezone

from apps.api.models import User, Book


class UserModelSchema(ModelSchema):
    class Meta:
        model = User
        exclude = ("password",)


class BookModelSchema(ModelSchema):
    class Meta:
        model = Book
        fields = "__all__"


# -------------------------------------------------------------------------------------------------------------------- #
# filter schema
# -------------------------------------------------------------------------------------------------------------------- #
class BookFilterSchema(FilterSchema):
    """
    [Django Ninja 官方文档 - 过滤](https://django-ninja.cn/guides/input/filtering/)

    # 在你的 API 处理程序中结合 Query 使用这个模式: （猜测，Query 似乎来自查询参数，不知道默认的查询参数使用会不会出问题）
    @api.get("/books")
    def list_books(request, filters: BookFilterSchema = Query(...)):
        books = Book.objects.all()
        books = filters.filter(books)
        return books

    # 在底层， FilterSchema 将其字段转换为 Q 表达式，然后将它们组合起来并用于过滤你的查询集。

    # 除了使用 .filter 方法，你也可以获取准备好的 Q表达式并自己进行过滤。
    # 当你在通过 API 向用户公开的内容之上还有一些额外的查询集过滤时，这可能会很有用：
    @api.get("/books")
    def list_books(request, filters: BookFilterSchema = Query(...)):

        # Never serve books from inactive publishers and authors
        q = Q(author__is_active=True) | Q(publisher__is_active=True)

        # But allow filtering the rest of the books
        q &= filters.get_filter_expression()
        return Book.objects.filter(q)

    默认情况下，过滤器将按照以下方式运行：
    - None 值将被忽略且不进行过滤；
    - 每个非 None 字段将根据每个字段的 Field 定义转换为一个 Q 表达式；
    - 所有的 Q 表达式将使用 AND 逻辑运算符合并为一个；
    - 生成的 Q 表达式用于过滤查询集，并返回一个应用了 .filter 子句的查询集给你。

    # Field 中设定 ignore_none=False 可以将 None 视为应该进行过滤的有效值。
    # tag: Optional[str] = Field(None, q='tag', ignore_none=False)
    # 这样，当用户没有为 "tag" 提供其他值时，过滤将始终包括 tag=None 条件。

    # 有时你可能希望有复杂的过滤场景，这些场景无法通过单个字段注释来处理。对于此类情况，你可以将你的字段过滤逻辑实现为自定义方法。
    # 只需定义一个名为 filter_<field_name> 的方法，该方法接受一个过滤值并返回一个 Q 表达式：
    class BookFilterSchema(FilterSchema):
        tag: Optional[str] = None
        popular: Optional[bool] = None

        def filter_popular(self, value: bool) -> Q:
            return Q(view_count__gt=1000) | Q(download_count__gt=100) if value else Q()
    # 此类字段方法优先于相应字段的 Field() 定义中指定的内容。
    如果这还不够，你可以在 custom_expression 方法中为整个 FilterSet 类实现你自己的自定义过滤逻辑：
    class BookFilterSchema(FilterSchema):
        name: Optional[str] = None
        popular: Optional[bool] = None

        def custom_expression(self) -> Q:
            q = Q()
            if self.name:
                q &= Q(name__icontains=self.name)
            if self.popular:
                q &= (
                    Q(view_count__gt=1000) |
                    Q(downloads__gt=100) |
                    Q(tag='popular')
                )
            return q
    """
    title: Optional[str] = Field(None, **{"q": "title__icontains"})
    author: Optional[str] = Field(None, **{"q": "author__icontains"})

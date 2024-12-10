from ninja import Router
from ninja.orm.factory import create_schema
from ninja_crud import views, viewsets

from apps.api.models import Book

router = Router(tags=["crud"])

book_router = Router(tags=["crud:book"])
router.add_router("/book", book_router)  # 多级路由/嵌套路由器


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

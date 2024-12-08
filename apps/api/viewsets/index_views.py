from ninja import Router

from apps.api.views import api

router = Router(tags=["index"])
api.add_router("", router)

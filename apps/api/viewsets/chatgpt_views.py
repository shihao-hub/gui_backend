from ninja import Router

from apps.api.views import api

router = Router(tags=["chatgpt"])
api.add_router("/chatgpt", router)

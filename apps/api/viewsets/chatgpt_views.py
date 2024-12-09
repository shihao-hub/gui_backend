from ninja import Router

from apps.api.shared.singleton import Singleton
from apps.core.shared.log import Log

api = Singleton.api
log = Log()

router = Router(tags=["chatgpt"])
api.add_router("/chatgpt", router)

from ninja import Router

from apps.api.shared.singleton import Singleton
from apps.api.shared.utils import generic_response, get_registered_router
from apps.core.shared.log import Log

api = Singleton.api
log = Log()

router = get_registered_router(api, __file__)
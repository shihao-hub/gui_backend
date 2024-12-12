from ninja import Router

from apps.api.shared.utils import generic_response, get_registered_router
from apps.core.shared.log import Log

log = Log()

router = Router(tags=["chatgpt"])

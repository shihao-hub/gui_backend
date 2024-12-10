from ninja import Router

from apps.api.viewsets.chatgpt import router as chatgpt_router
from apps.api.viewsets.crud import router as crud_router
from apps.api.viewsets.exercise import router as exercise_router
from apps.api.viewsets.redis import router as redis_router
from apps.api.viewsets.task import router as task_router
from apps.api.viewsets.tool import router as tool_router

router = Router()

router.add_router("/chatgpt", chatgpt_router)  # "apps.api.viewsets.chatgpt" 为什么不行？
router.add_router("/crud", crud_router)
router.add_router("/exercise", exercise_router)
router.add_router("/redis", redis_router)
router.add_router("/task", task_router)
router.add_router("/tool", tool_router)

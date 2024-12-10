from ninja import Router

router = Router()

router.add_router("/chatgpt", "apps.api.viewsets.chatgpt.router")
router.add_router("/crud", "apps.api.viewsets.crud.router")
router.add_router("/exercise", "apps.api.viewsets.exercise.router")
router.add_router("/redis", "apps.api.viewsets.redis.router")
router.add_router("/task", "apps.api.viewsets.task.router")
router.add_router("/tool", "apps.api.viewsets.tool.router")

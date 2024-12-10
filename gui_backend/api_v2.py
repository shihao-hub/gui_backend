from ninja import NinjaAPI

from apps.ninja_tool.api import router as tool_router

api = NinjaAPI(version="2.0.0")

api.add_router("/tool", tool_router)

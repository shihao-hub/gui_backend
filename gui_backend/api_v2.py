import orjson

from ninja import NinjaAPI
from ninja.parser import Parser
from ninja.security import HttpBearer


class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


api = NinjaAPI(
    version="2.0.0",
    parser=ORJSONParser(),
    csrf=True,
    auth=[GlobalAuth()]
)

api.add_router("/exercise", "apps.ninja_exercise.api.router")
api.add_router("/tool", "apps.ninja_tool.api.router")

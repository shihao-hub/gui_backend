import orjson
from ninja import NinjaAPI, Redoc
from ninja.parser import Parser
from ninja_extra import NinjaExtraAPI


# Redoc -> 另一个自动生成的文档(由Redoc 提供)，看起来也还行，但是字体太小了... 放大一点勉强还行... 但是还是一般...

# https://django-ninja.cn/guides/input/request-parsers/
# orjson 是一个用于 Python 的快速、准确的 JSON 库。
# 它在基准测试中是最快的 Python JSON 库，并且比标准的 json 库或其他第三方库更准确。
class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


class Singleton:
    api = NinjaExtraAPI(docs=Redoc(), parser=ORJSONParser())  # 不知道 NinjaExtraAPI 是单纯的 NinjaAPI 扩充还是？

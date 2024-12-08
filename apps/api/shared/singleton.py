from ninja import NinjaAPI
from ninja_extra import NinjaExtraAPI


class Singleton:
    api = NinjaExtraAPI()  # 2024-12-08：不知道 NinjaExtraAPI 是单纯的 NinjaAPI 扩充还是？

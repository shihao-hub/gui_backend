import os
import warnings
from typing import List

from ninja import NinjaAPI, Router

from apps.api.schemasets import SuccessSchema, ErrorSchema

generic_response = {200: SuccessSchema, 400: ErrorSchema}


# 2024-12-09：
# 形如 api.get(response=generic_response) 重复度太高，
# 以我目前的理解，返回 success、error Response 更方便
# ninja 提供 response 肯定由它的道理的，只是我不太理解罢了
# 猜测1：可能是为了 api/docs 详细点？但我直接约定不行吗？默认 200、400 的结构。约定大于配置不好吗？何必代码里重复那么多？


def get_registered_router(api: NinjaAPI, file: str, extra_tags: List = None) -> Router:
    warnings.warn(
        "deprecated_function is deprecated and will be removed in a future version.",
        DeprecationWarning,
    )
    # 2024-12-10：这个不太好，隐藏了许多东西。直接手写并没有太麻烦！如非必要，勿增实体！
    main_tag = os.path.splitext(os.path.basename(file))[0]
    extra_tags = extra_tags if extra_tags else []

    tags = [main_tag]

    for e in extra_tags:
        if e not in tags:
            tags.append(e)

    router = Router()
    api.add_router(f"/{main_tag}", router, tags=tags)
    return router

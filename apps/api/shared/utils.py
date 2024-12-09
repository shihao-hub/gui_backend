from typing import Dict, Optional

from ninja.responses import Response

from apps.api.schemasets import SuccessSchema, ErrorSchema

generic_success_error_responses = {200: SuccessSchema, 400: ErrorSchema}


def _create_response(success: bool, response_dict: Dict) -> Response:
    status = 200 if success else 400
    json_data = generic_success_error_responses.get(status)(**response_dict).dict()
    return Response(json_data, status=status)


# 2024-12-09：
# 形如 api.get(response=generic_success_error_responses) 重复度太高，
# 以我目前的理解，返回 success、error Response 更方便
# ninja 提供 response 肯定由它的道理的，只是我不太理解罢了
# 猜测1：可能是为了 api/docs 详细点？但我直接约定不行吗？默认 200、400 的结构。约定大于配置不好吗？何必代码里重复那么多？

def _insert_if_exist(inst: Dict, key: str, value):
    if value:
        inst[key] = value


def success_response(_: Optional[Dict] = None, message=None, data=None) -> Response:
    # 响应结构为 SuccessSchema 的结构
    # response_dict（即第一个参数） 似乎不需要再用了，此处保留是为了兼容之前的代码
    # 虽然强迫症可能会绝对难受，但是编程就是如此。哪怕一个小项目，也会因为之前的代码而苦恼...
    response_dict = _ if _ else {}

    _insert_if_exist(response_dict, "message", message)
    _insert_if_exist(response_dict, "data", data)

    return _create_response(True, response_dict)


def error_response(_: Optional[Dict] = None, message=None, reason=None, data=None) -> Response:
    response_dict = _ if _ else {}

    _insert_if_exist(response_dict, "message", message)
    _insert_if_exist(response_dict, "reason", reason)
    _insert_if_exist(response_dict, "data", data)

    return _create_response(False, response_dict)

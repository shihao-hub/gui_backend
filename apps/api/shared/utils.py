from typing import Dict

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

def success_response(response_dict: Dict) -> Response:
    return _create_response(True, response_dict)


def error_response(response_dict: Dict) -> Response:
    return _create_response(False, response_dict)

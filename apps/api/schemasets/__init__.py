from typing import Literal, Optional, List, Dict, Union, Any

from ninja import Schema


class SuccessSchema(Schema):
    """
    {
        "success": True,
        "message": "Books retrieved successfully.",
        "data": [],
        "meta": {
            "requestId": "abc124",
            "timestamp": "2023-10-01T12:35:00Z"
        },
        "errors": null,
    }
    """
    success: bool = True
    message: str = ""
    data: Union[Dict, List, str, int, float, None] = None

    meta: Optional[Dict] = None  # 可能的附加信息，如分页信息或其他元数据。 -> meta["timestamp"] = timezone.now()
    errors: None = None


class ErrorSchema(Schema):
    """
    {
        "success": False,
        "message": "The user with ID 1 was not found.",
        "data": null,
        "meta": {
            "requestId": "abc126",
            "timestamp": "2023-10-01T12:36:00Z"
        },
        "errors": [
            {
                "code": "USER_NOT_FOUND",
                "message": "The user with ID 1 was not found.",
                "details": {
                    "requestedId": 1
                }
            }
        ],
    }
    """
    success: bool = False
    message: str = ""
    data: Union[Dict, List, str, int, float, None] = None

    meta: Optional[Dict] = None  # 可能的附加信息，如分页信息或其他元数据。
    errors: Optional[List[Dict]] = None  # 可能的错误信息，如验证错误等。

from typing import List

from django.http import HttpRequest
from ninja import Router, Form, File, UploadedFile
from ninja_extra import api_controller, http_get, http_post, http_put, http_delete

from apps.api.exceptions import BadRequestError
from apps.api.shared.utils import generic_response
from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

log = Log()

router = Router(tags=["ocr"])


@router.post("/orc_one_image", response=generic_response, summary="ocr 一张图片")
def orc_one_image(request: HttpRequest, image: File[UploadedFile]):
    pass

import uuid
from typing import List

from PIL import Image
import pytesseract

from django.conf import settings
from django.http import HttpRequest
from django.core.files.storage import FileSystemStorage
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
    location = str(settings.BASE_DIR / f"temporary")
    fs = FileSystemStorage(location=location)
    filename = f"{uuid.uuid4()}-{image.name}"
    fs.save(filename, image.file)
    image = Image.open(fs.path(filename))
    text = pytesseract.image_to_string(image, lang="chi_sim")
    return {"data": text}

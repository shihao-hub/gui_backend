import os
import uuid
from io import BytesIO
from typing import Optional

import chardet
import pangu
from ninja import Router, UploadedFile, File, Schema

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, FileResponse

from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

log = Log()

router = Router(tags=["tool"])


class FormatMarkDownResp(Schema):
    # TODO: 不止能不能这样
    file: UploadedFile


@router.post("/format_markdown", summary="格式化 markdown 文件")
@knowledge("FileSystemStorage", "探测编码 chardet.detect", "BytesIO seek(0)", "FileResponse")
def format_markdown(request: HttpRequest, file: File[UploadedFile], grave_accent: Optional[bool] = None):
    """
    格式化 markdown 文件
    - 中英文间隔一个空格，形如标题这般
    - 增加开关，用于控制是否需要在英文句子的前后加 "```"
    """
    # TODO: 封装成类
    # location = str(settings.BASE_DIR / "file_system_storage_location")
    # fs = FileSystemStorage(location=location)
    # filename = fs.save(f"{uuid.uuid4()}-{file.name}", file)
    # file_url = fs.url(filename)

    # 探测编码
    text_bytes = file.read()
    encoding = chardet.detect(text_bytes).get("encoding")  # utf-8

    # 关键逻辑，但是似乎是存在问题的...
    content = pangu.spacing_text(text_bytes.decode(encoding))

    bytes_io = BytesIO()
    bytes_io.write(content.encode(encoding))
    bytes_io.seek(0)  # 记得 seek(0)，否则返回的文件为空

    return FileResponse(bytes_io, as_attachment=True, filename=file.name)

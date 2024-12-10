import base64
import functools
import os.path
import sqlite3
import traceback
from pathlib import Path
from typing import List, Literal, Optional

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from ninja import Router, UploadedFile, File, Form

from apps.api import settings as app_settings
from apps.api.exceptions import BadRequestError
from apps.api.schemasets import SuccessSchema
from apps.api.schemasets.tool import Base64Request, Base64Response
from apps.api.shared.utils import generic_response
from apps.core.shared.log import Log

log = Log()

router = Router(tags=["tool"])


@router.post("/format_markdown", response=generic_response, summary="格式化 markdown 文件")
def format_markdown(request: HttpRequest, grave_accent: Optional[bool] = None, file: UploadedFile = File(...)):
    """
    格式化 markdown 文件
    - 中英文间隔一个空格，形如标题这般
    - 增加开关，用于控制是否需要在英文句子的前后加 "```"
    """
    return {"data": file.read().decode("utf-8")}


@router.get("/base64_encoding_list", response=generic_response, summary="获得支持的编码列表")
def get_base64_encoding_list(request: HttpRequest):
    encoding_enum = Base64Request.ResponseEncodingEnum
    data = [e.value for e in encoding_enum]
    return {"data": data}


@router.post("/encode_or_decode_base64", response=generic_response, summary="Base64 编解码")
def encode_or_decode_base64(request: HttpRequest, data: Base64Request):
    text: str = data.get_pending_text()

    if data.mode == Base64Request.ModeEnum.ENCODE:
        text_bytes: bytes = text.encode(data.response_encoding.value)
        base64_encoded: bytes = base64.b64encode(text_bytes)

        encoded_text: str = base64_encoded.decode(data.response_encoding.value)

        res = encoded_text
    else:

        base64_decoded: bytes = base64.b64decode(text)

        decoded_text = base64_decoded.decode(data.response_encoding.value)

        res = decoded_text
    # TODO: 能不能设置成嵌套呢？自动识别 data 是 ToolsBase64ResponseSchema 类型，我只需要传入 {"data": { "text": res }}
    return {"data": Base64Response(text=res).dict()}


def _get_file_path_by_sqlite_memory_mode(name: str) -> Path:
    resource_path = app_settings.RESOURCES
    if not os.path.splitext(name)[1]:
        name = name + ".gitignore"
    file_path: Path = resource_path / f"gitignore/{name}"

    # 2024-12-08：练习一下 sqlite3 的内存数据库，避免遗忘 -> sqlite3.connect(":memory:")
    # 所以 sqlite3 咋实现的，因为小项目用它都够了，这么轻量，感觉好厉害！
    # https://www.runoob.com/sqlite/sqlite-insert.html
    with sqlite3.connect(":memory:") as connect:
        cursor = connect.cursor()
        cursor.executescript("""
        CREATE TABLE memory_cache(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT
        );
        """)
        cursor.execute("INSERT INTO memory_cache(file_path) VALUES(?)", (str(file_path),))
        cursor.execute("SELECT * FROM memory_cache")
        res = Path(cursor.fetchone()[1])
    return res


@router.get("/get_gitignore_file/{name}", response=generic_response, summary="获得 gitignore 文件")
def get_gitignore_file(request: HttpRequest, name: str):
    file_path = _get_file_path_by_sqlite_memory_mode(name)
    if not file_path.exists():
        cache_key = "api:tools:gitignore:file_list"
        data = cache.get(cache_key, None)
        if data is None:
            # 得到所有 .gitignore 文件的文件名
            data = []
            for _, _, filenames in os.walk(str(app_settings.RESOURCES / "gitignore")):
                # cur_dir_path, sub_dirs, filenames
                data += filenames
                break
            # 目前是内存缓存，未设置 django 的 redis 缓存
            cache.set(cache_key, data, 60 * 60 * 12)
        log.info(data)
        raise BadRequestError(f"{name} 文件不存在")
    with file_path.open("r", encoding="utf-8") as file:
        response = HttpResponse(content_type="application/octet-stream")
        response.write(file.read().encode("utf-8"))
        response["Content-Disposition"] = f"attachment; filename={file_path.name}"
    return response

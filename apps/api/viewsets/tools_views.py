import logging
import base64
import os.path
import sqlite3
from pathlib import Path
from typing import Callable

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from ninja import Router, UploadedFile

from apps.api.views import api
from apps.api.schemas import ToolsBase64RequestSchema, ToolsBase64ResponseSchema, ErrorSchema
from apps.api import settings as app_settings

router = Router(tags=["tools"])
api.add_router("/tools", router)


@router.get("/base64_encoding_list", summary="获得支持的编码列表")
def get_base64_encoding_list(request: HttpRequest):
    encoding_enum = ToolsBase64RequestSchema.ResponseEncodingEnum
    data = [e.value for e in encoding_enum]
    return {"data": data}


@router.post("/base64", response={200: ToolsBase64ResponseSchema}, summary="Base64 编解码")
def handle_base64(request: HttpRequest, data: ToolsBase64RequestSchema):
    text: str = data.get_pending_text()

    if data.mode == ToolsBase64RequestSchema.ModeEnum.ENCODE:
        text_bytes: bytes = text.encode(data.response_encoding.value)
        base64_encoded: bytes = base64.b64encode(text_bytes)

        encoded_text: str = base64_encoded.decode(data.response_encoding.value)

        res = encoded_text
    else:

        base64_decoded: bytes = base64.b64decode(text)

        decoded_text = base64_decoded.decode(data.response_encoding.value)

        res = decoded_text
    return {"text": res}


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


@router.get("/gitignore/{name}", response={400: ErrorSchema}, summary="获得 gitignore 文件")
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

        return 400, {"message": f"{name} 文件不存在", "data": data}
    with file_path.open("r", encoding="utf-8") as file:
        response = HttpResponse(content_type="application/octet-stream")
        response.write(file.read().encode("utf-8"))
        response["Content-Disposition"] = f"attachment; filename={file_path.name}"
    return response

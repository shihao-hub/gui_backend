import base64
import functools
import os.path
import re
import sqlite3
import traceback
from pathlib import Path
from re import Pattern
from typing import List, Literal

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from ninja import Router, UploadedFile, File, Form
from ninja_extra import api_controller, http_post

from apps.api import settings as app_settings
from apps.api.schemasets.tools_schemas import ToolsBase64RequestSchema, ToolsBase64ResponseSchema
from apps.api.shared.utils import success_response, error_response
from apps.api.shared.singleton import Singleton
from apps.core.shared.log import Log

api = Singleton.api
log = Log()
router = Router(tags=["tools"])
api.add_router("/tools", router)


@api_controller("/tools/comment_collector", tags=["tools:comment_collector"])
class CommentCollector:
    def _collect_comments_by_pattern(self, pattern: Pattern, content: str) -> List[str]:
        this = self

        res = []
        matches = pattern.findall(content)
        for match in matches:
            res.append(match.strip())  # 清除空白符
        return res

    @staticmethod
    def _collect_comment_notes_exception_handler(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"{e}\n{traceback.format_exc()}")
                return error_response({"message": "筛选文件中符合条件的注释功能，发生错误"})

        return wrapper

    @http_post("/collect_comments", summary="筛选文件中符合条件的注释")
    @_collect_comment_notes_exception_handler
    def collect_comment_notes(self,
                              request: HttpRequest,
                              # mode: Literal["Q", "N", "TD"] = Form(...), # form_data
                              mode: Literal["Q", "N", "TD"],  # query_parameters/path_parameters
                              files: List[UploadedFile] = File(...)):

        # file 只能被消耗一次。此处如果启用的话，file 被消耗后再使用就是 b'' 空文件！
        # fs = FileSystemStorage(location=str(settings.BASE_DIR / "temporary"))  # django 的文件系统
        # filename = fs.save(file.name, file)
        # file_url = fs.url(filename)  # 文件路径
        # log.info(file_url)

        res = {}
        for file in files:
            content: bytes = file.read()
            content_str = content.decode("utf-8")
            res.setdefault(file.name, [])
            res[file.name] += self._collect_comments_by_pattern(re.compile(rf"\({mode}\)!:\s*(.*)"), content_str)

        return success_response({"data": res})


@router.get("/base64_encoding_list", summary="获得支持的编码列表")
def get_base64_encoding_list(request: HttpRequest):
    encoding_enum = ToolsBase64RequestSchema.ResponseEncodingEnum
    data = [e.value for e in encoding_enum]
    return success_response({"data": data})


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
    return success_response(data={"text": res})


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


@router.get("/gitignore/{name}", summary="获得 gitignore 文件")
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

        return error_response({"message": f"{name} 文件不存在", "data": data})
    with file_path.open("r", encoding="utf-8") as file:
        response = HttpResponse(content_type="application/octet-stream")
        response.write(file.read().encode("utf-8"))
        response["Content-Disposition"] = f"attachment; filename={file_path.name}"
    return response


api.register_controllers(
    CommentCollector
)

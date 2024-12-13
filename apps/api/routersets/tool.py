import base64
import functools
import os.path
import re
import shutil
import sqlite3
import traceback
import uuid
import zipfile
from io import BytesIO, IOBase
from pathlib import Path
from typing import List, Literal, Optional, BinaryIO

import chardet
import pangu

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, FileResponse
from ninja import Router, UploadedFile, File, Query
from ninja.errors import HttpError
from ninja.decorators import decorate_view
from ninja_extra import api_controller, http_post, http_get, http_put, http_delete, http_patch

from apps.api import settings as app_settings
from apps.api.exceptions import BadRequestError
from apps.api.schemasets import SuccessSchema
from apps.api.schemasets.tool import Base64Request, Base64Response, FormatMarkDownRequestQuery
from apps.api.shared.utils import generic_response
from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

log = Log()

router = Router(tags=["tool"])


@api_controller("/tool/comment_collector", tags=router.tags)
class CommentCollectorController:

    @staticmethod
    def decorator_collect_comment_notes_exception_handler(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"{e}\n{traceback.format_exc()}")
                raise BadRequestError(f"筛选文件中符合条件的注释功能，发生错误") from e

        return wrapper

    class CollectCommentsFObj:
        @staticmethod
        def is_text_file(file: BinaryIO) -> bool:
            # 判断一个文件是文本文件 -> 2024-12-12-23:52：随便找个压缩包测出来的 bug
            rawdata = file.read(10000)  # 读取一部分数据进行检测
            file.seek(0)
            result = chardet.detect(rawdata)
            # 如果检测结果的置信度大于某个阈值，且推测的编码不是常见的二进制编码，则可能是文本文件
            return result.get("confidence", 0) > 0.9 and result.get("encoding") is not None

        @staticmethod
        def is_zip_file(name: str) -> bool:
            # 如果文件是压缩包，暂定 .zip
            return name.endswith(".zip")

        def __init__(self, mode: Literal["Question", "Note"], files: List[UploadedFile]):
            self.mode = mode
            self.files = files

        def _collect_comments_by_pattern(self, pattern: re.Pattern, content: str) -> List[str]:
            this = self

            res = []
            matches = pattern.findall(content)
            for match in matches:
                res.append(match.strip())  # 清除空白符
            return res

        def get_comments(self, file: BytesIO):
            content: bytes = file.read()
            # log.info(f"{_file} -> {content}")
            content_str = content.decode(chardet.detect(content).get("encoding"))
            return self._collect_comments_by_pattern(re.compile(rf"\({self.mode[0]}\)!:\s*(.*)"), content_str)

        def handle_zip_file(self, file: UploadedFile) -> dict:
            res = {}

            zip_target_path = settings.BASE_DIR / "temporary" / str(uuid.uuid4())
            try:
                with zipfile.ZipFile(BytesIO(file.read())) as zf:

                    zf.extractall(path=zip_target_path)
                    # 文件解压缩后，遍历读取每个文件，重复操作
                    for dir_path, sub_dirs, filenames in os.walk(zip_target_path):
                        for name in filenames:
                            # 注意，此处显然可以优化，这个文件可以封装成二进制读写
                            with open(os.path.join(dir_path, name), "rb") as f:
                                if not self.is_text_file(f):
                                    continue
                                key = os.path.join(dir_path, name).replace(str(zip_target_path), "")
                                # TODO: 压缩包重名了怎么办？这显然有问题（测试的重要性...程序的健壮性显然需要）
                                res.setdefault(key, [])
                                res[key] += self.get_comments(BytesIO(f.read()))
            finally:
                if zip_target_path.is_dir():
                    shutil.rmtree(zip_target_path)

            return res

        def run(self):

            # file 只能被消耗一次。此处如果启用的话，file 被消耗后再使用就是 b'' 空文件！
            # fs = FileSystemStorage(location=str(settings.BASE_DIR / "temporary"))  # django 的文件系统
            # filename = fs.save(file.name, file)
            # file_url = fs.url(filename)  # 文件路径
            # log.info(file_url)

            # file 需要增加校验，必须是文本文件

            res = {}
            for file in self.files:
                if self.is_zip_file(file.name):
                    res.update(self.handle_zip_file(file))
                    continue
                bytes_io = BytesIO(file.read())
                if not self.is_text_file(bytes_io):
                    continue
                res.setdefault(file.name, [])
                res[file.name] += self.get_comments(bytes_io)

            return {"data": res}

    @http_post("/collect_comments", response=generic_response, summary="筛选文件中符合条件的注释")
    @decorate_view(decorator_collect_comment_notes_exception_handler)
    @knowledge("zipfile 解压缩到临时文件并 finally 删除目录", "BytesIO 等价于内存文件", "os.walk 迭代遍历整个文件目录")
    def collect_comments(self,
                         request: HttpRequest,
                         # mode: Literal["Q", "N"] = Form(...), # form_data
                         mode: Literal["Question", "Note"],  # query_parameters/path_parameters
                         # files: List[UploadedFile] = File(...)): -> ninja 0.x.x 版本
                         files: File[List[UploadedFile]]):

        return self.CollectCommentsFObj(mode, files).run()


# 注意，一个文件中的函数请勿重名
# Warning: operation_id "apps_api_viewsets_tool_format_markdown" is already used
# (Try giving a different name to: apps.api.viewsets.tool.format_markdown)


@router.post("/format_markdown", summary="格式化 markdown 文件")
@knowledge("FileSystemStorage", "探测编码 chardet.detect", "BytesIO seek(0)")
@knowledge("FileResponse", "UploadedFile 仅消耗一次", "使用模式来封装查询参数 Query[Schema]")
@knowledge("raise HttpError(status_code, message)")
def format_markdown(request: HttpRequest, query: Query[FormatMarkDownRequestQuery], file: File[UploadedFile]):
    """
    格式化 markdown 文件
    - 中英文间隔一个空格，形如标题这般
    - 增加开关，用于控制是否需要在英文句子的前后加 "```"
    """
    # TODO: 封装成类
    location = str(settings.BASE_DIR / f"file_system_storage_location/{timezone.now().strftime('%Y-%m-%d')}")
    fs = FileSystemStorage(location=location)
    filename = fs.save(f"{uuid.uuid4()}-{file.name}", file)
    file_url = fs.url(filename)

    with fs.open(filename) as f:
        text_bytes = f.read()

    # 探测编码
    encoding = chardet.detect(text_bytes).get("encoding")  # utf-8...
    if len(text_bytes) != 0 and encoding is None:
        raise HttpError(400, "未探测到文件的编码！")

    # 关键逻辑，但是似乎是存在问题的...
    content = pangu.spacing_text(text_bytes.decode(encoding))

    bytes_io = BytesIO()
    bytes_io.write(content.encode(encoding))
    bytes_io.seek(0)  # 记得 seek(0)，否则返回的文件为空

    return FileResponse(bytes_io, as_attachment=True, filename=file.name)


@router.get("/base64_encoding_list", response=generic_response, summary="获得支持的编码列表")
@decorate_view(cache_page(60))  # 缓存 60s，注意，ninja 的 view_func 返回值可能不是 response，因此需要包装一下
@knowledge("缓存静态结果 cache_page")
def get_base64_encoding_list(request: HttpRequest):
    log.info("call get_base64_encoding_list")
    encoding_enum = Base64Request.ResponseEncodingEnum
    data = [e.value for e in encoding_enum]
    return {"data": data}


@router.post("/encode_or_decode_base64", response=generic_response, summary="Base64 编解码")
@knowledge("base64 b64encode b64decode")
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


@knowledge("sqlite3 :memory:")
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
@knowledge("cache set get expired_time")
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

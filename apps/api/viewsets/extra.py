import functools
import re
import traceback
from typing import Literal, List

from re import Pattern

import redis

from django.http import HttpRequest
from ninja import File, UploadedFile
from ninja.decorators import decorate_view
from ninja_extra import api_controller, http_post
from ninja_extra import api_controller, http_get, http_post, http_put, http_delete

from apps.api.exceptions import BadRequestError
from apps.api.schemasets import SuccessSchema
from apps.api.schemasets.redis import TodoListItemSchema
from apps.api.shared.utils import generic_response
from apps.core.shared.log import Log
from gui_backend.api import api

log = Log()

db = redis.StrictRedis(host="localhost", port=6379, db=0)


# -------------------------------------------------------------------------------------------------------------------- #
# ninja_extra 的 api_controller（ninja_extra 提供了一种 基于类 的方法以及额外的功能，这将加速您的 RESTful API 开发。）
# -------------------------------------------------------------------------------------------------------------------- #
# 这里不兼容这个 router... 麻烦
@api_controller("/redis/todolist", tags=["redis:todolist"], permissions=[])
class TodoListController:
    # 此处的代码是随便让 gpt 提供的 redis 代码，结构是不正确的。毕竟 list 存可以，删怎么办，序号都变了
    # 欸，不对。序号变了也没问题，如果有前端的话。每次删除都会重新调用查询接口啊？那怕什么呢？

    TODO_LIST_KEY = "api:redis:todo_list"  # redis list

    @http_post("/add", response=generic_response, summary="添加待办事项")
    def add_todo(self, request: HttpRequest, data: TodoListItemSchema):
        value = data.value
        res = db.rpush(self.TODO_LIST_KEY, value.encode("utf-8"))
        data = {"id": str(res)}
        return {"data": data}

    @http_get("/list", response=generic_response, summary="查看所有待办事项")
    def view_todos(self):
        todos = db.lrange(self.TODO_LIST_KEY, 0, -1)
        # 注意，返回的 todos 是 bytes 列表，需要转为 str 才能被 JSON 序列化
        return {"data": [e.decode("utf-8") for e in todos]}

    @http_delete("/delete", response=generic_response, summary="删除指定索引的待办事项")
    def delete_todo(self, request: HttpRequest, index: int):
        todos = db.lrange(self.TODO_LIST_KEY, 0, -1)
        # check the index range
        if index < 1 or index > len(todos):
            raise BadRequestError("Out of index range")
        todo_task_delete = todos[index - 1]
        db.lrem(self.TODO_LIST_KEY, 1, todo_task_delete)
        return {"message": f"delete todo task: {index} successfully."}


# -------------------------------------------------------------------------------------------------------------------- #
# ninja_extra
# -------------------------------------------------------------------------------------------------------------------- #
@api_controller("/tool/comment_collector", tags=["tool:comment_collector"])
class CommentCollector:
    def _collect_comments_by_pattern(self, pattern: Pattern, content: str) -> List[str]:
        this = self

        res = []
        matches = pattern.findall(content)
        for match in matches:
            res.append(match.strip())  # 清除空白符
        return res

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

    @http_post("/collect_comments", response=generic_response, summary="筛选文件中符合条件的注释")
    @decorate_view(decorator_collect_comment_notes_exception_handler)
    def collect_comment_notes(self,
                              request: HttpRequest,
                              # mode: Literal["Q", "N"] = Form(...), # form_data
                              mode: Literal["Q", "N"],  # query_parameters/path_parameters
                              # files: List[UploadedFile] = File(...)): -> ninja 0.x.x 版本
                              files: File[List[UploadedFile]]):

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

        return {"data": res}


api.register_controllers(
    CommentCollector
)

api.register_controllers(TodoListController)

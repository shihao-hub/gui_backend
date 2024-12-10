import json

import redis
from django.http import HttpRequest

from ninja_extra import api_controller, http_get, http_post, http_put, http_delete

from apps.api.exceptions import BadRequestError
from apps.api.schemas import RedisTodoListItemSchema, SuccessSchema
from apps.api.shared.singleton import Singleton
from apps.api.shared.utils import generic_response, get_registered_router
from apps.core.shared.log import Log

api = Singleton.api
log = Log()

router = get_registered_router(api, __file__)

db = redis.StrictRedis(host="localhost", port=6379, db=0)


@router.get("/test", summary="api:redis:test")
def test(request: HttpRequest):
    pass


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
    def add_todo(self, request: HttpRequest, data: RedisTodoListItemSchema):
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


api.register_controllers(TodoListController)

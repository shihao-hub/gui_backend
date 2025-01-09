import functools
import re
from typing import List

from django.http import HttpRequest
from ninja import Router, Form
from ninja_extra import api_controller, http_get, http_post, http_put, http_delete

from apps.api.exceptions import BadRequestError
from apps.api.settings import redis_db as db
from apps.api.schemasets.redis import TodoListItemSchema, TodoListItemV2Schema
from apps.api.shared.utils import generic_response
from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

log = Log()

router = Router(tags=["redis"])


@api_controller("/redis/quicknote", tags=router.tags, permissions=[])
class QuickNoteController:
    REDIS_KEY = "api:redis:quick_note"

    def _check_index(self, index: int, list_len: int = None):
        this = self

        if list_len is None:
            list_len = db.llen(self.REDIS_KEY)

        # check the index range
        if index < 0 or index >= list_len:
            raise BadRequestError("Out of index range")

    def _remove_element_by_index(self, index: int):
        # lua script：使用 lrange 找出不需要删除的元素，然后将旧列表删除，创建新列表...（redis 服务器有影响，web 服务器没影响）
        lua_script = """
            local index = tonumber(ARGV[1])
            local list_key = KEYS[1]
            local len = redis.call("LLEN", list_key)
    
            if index < 0 then
                index = len + index  -- 处理负索引
            end
    
            if index >= len or index < 0 then
                return nil  -- 索引超出范围
            end
    
            redis.log(redis.LOG_NOTICE, "index: " .. index)
    
            local first_part, second_part
            if index == 0 then
                -- 如果 index 是 0，直接处理。因为 redis.call("LRANGE", list_key, 0, index - 1) 返回的不是空列表！
                first_part = {}
                second_part = redis.call("LRANGE", list_key, 1, -1)  -- 从 1 到 -1 获取后面的部分
            else
                first_part = redis.call("LRANGE", list_key, 0, index - 1)
                second_part = redis.call("LRANGE", list_key, index + 1, -1)
            end
    
            redis.call("DEL", list_key)  -- 删除原列表
            for _, v in ipairs(first_part) do
                redis.call("RPUSH", list_key, v)  -- 重新添加前面的部分
            end
    
            for _, v in ipairs(second_part) do
                redis.call("RPUSH", list_key, v)  -- 重新添加后面的部分
            end
    
            return 1  -- 返回成功
        """
        return db.eval(lua_script, 1, self.REDIS_KEY, index)

    @http_get("", response=generic_response)
    def list_todo(self):

        items: List[bytes] = db.lrange(self.REDIS_KEY, 0, -1)
        data: List[str] = [e.decode("utf-8") for e in items]
        # cmp = functools.cmp_to_key(lambda x, y: len(x) - len(y))
        # data.sort(key=cmp)
        return {"data": data}

    @http_post("", response=generic_response)
    def create_todo(self, request: HttpRequest, value: Form[str]):
        index = db.rpush(self.REDIS_KEY, value.encode("utf-8"))
        return {"data": {"index": index}}

    @http_delete("/delete", response=generic_response)
    def delete_todo(self, request: HttpRequest, index: int):
        if self._remove_element_by_index(index) is None:
            return 400, {"message": f"delete todo task: {index} failed."}

        return {"message": f"delete todo task: {index} successfully."}

    @http_post("/{index}", response=generic_response)
    def update_todo(self, request: HttpRequest, index: int, content: Form[str]):
        self._check_index(index)

        db.lset(self.REDIS_KEY, index, content)
        return {"message": f"update todo task: {index} successfully."}

    @http_get("/{index}", response=generic_response)
    def get_todo(self, request: HttpRequest, index: int):
        self._check_index(index)
        data = db.lrange(self.REDIS_KEY, index, index)
        return {"data": data[0].decode("utf-8")}


# TODO:
#   ninja_extra 注册的时候，似乎都是同一个函数。所以这代码似乎无法复用...
#   原理是啥？
#   题外话，关于重复代码，我应该遵循事不过三，第三次重复再考虑复用！
# @api_controller("/redis/todolist", tags=router.tags, permissions=[])
# class TodoListController(TodoListQuickNoteMixin):
#     REDIS_KEY = TodoListQuickNoteMixin.REDIS_KEY.format(project="todo_list")


# TODO: 这个放到 django 的 views.py 里如何？感觉可以（理由是 ninja_extra 使用的不是路由，很讨厌）
# TODO: 用前端技术实现一个 todolist 页面，关键元素：列表、增、删、改
@api_controller("/redis/todolist", tags=router.tags, permissions=[])
class TodoListController:
    # QUESTION:
    #   此处的代码是随便让 gpt 提供的 redis 代码，结构是不正确的。毕竟 list 存可以，删怎么办，序号都变了
    #   欸，不对。序号变了也没问题，如果有前端的话。每次删除都会重新调用查询接口啊？那怕什么呢？

    TODO_LIST_KEY = "api:redis:todo_list"  # redis list

    # TODO_LIST_KEY_COUNTER = "api:redis:todo_list_counter"  # redis counter

    def _check_index(self, index: int, list_len: int = None):
        this = self

        if list_len is None:
            list_len = db.llen(self.TODO_LIST_KEY)

        # check the index range
        if index < 0 or index >= list_len:
            raise BadRequestError("Out of index range")

    def _remove_element_by_index(self, index: int):
        # lua script：使用 lrange 找出不需要删除的元素，然后将旧列表删除，创建新列表...（redis 服务器有影响，web 服务器没影响）
        lua_script = """
            local index = tonumber(ARGV[1])
            local list_key = KEYS[1]
            local len = redis.call("LLEN", list_key)
            
            if index < 0 then
                index = len + index  -- 处理负索引
            end
            
            if index >= len or index < 0 then
                return nil  -- 索引超出范围
            end
            
            redis.log(redis.LOG_NOTICE, "index: " .. index)
            
            local first_part, second_part
            if index == 0 then
                -- 如果 index 是 0，直接处理。因为 redis.call("LRANGE", list_key, 0, index - 1) 返回的不是空列表！
                first_part = {}
                second_part = redis.call("LRANGE", list_key, 1, -1)  -- 从 1 到 -1 获取后面的部分
            else
                first_part = redis.call("LRANGE", list_key, 0, index - 1)
                second_part = redis.call("LRANGE", list_key, index + 1, -1)
            end
            
            redis.call("DEL", list_key)  -- 删除原列表
            for _, v in ipairs(first_part) do
                redis.call("RPUSH", list_key, v)  -- 重新添加前面的部分
            end
            
            for _, v in ipairs(second_part) do
                redis.call("RPUSH", list_key, v)  -- 重新添加后面的部分
            end
    
            return 1  -- 返回成功
        """
        return db.eval(lua_script, 1, self.TODO_LIST_KEY, index)

    @http_get("", response=generic_response, summary="查看所有待办事项")
    @knowledge("str.replace 不支持正则表达式，可以用 re.sub 替代")
    def list_todo(self):
        # TODO: 每次项目运行完的第一次请求，应该清空 key，然后执行某个序列化后的文件？
        # if DEBUG

        todos: List[bytes] = db.lrange(self.TODO_LIST_KEY, 0, -1)
        # 注意，返回的 todos 是 bytes 列表，需要转为 str 才能被 JSON 序列化
        return {"data": [re.sub(r"^.*\\|", "", e.decode("utf-8"), 1) for e in todos]}

    @http_post("", response=generic_response, summary="增 - 待办事项")
    def create_todo(self, request: HttpRequest, value: Form[str]):
        index = db.rpush(self.TODO_LIST_KEY, value.encode("utf-8"))
        return {"data": {"index": index}}

    @http_delete("/delete", response=generic_response, summary="删 - 指定索引的待办事项")
    @knowledge("我认为 软删除 + 定期清除是更好的办法...")
    def delete_todo(self, request: HttpRequest, index: int):
        if self._remove_element_by_index(index) is None:
            return 400, {"message": f"delete todo task: {index} failed."}

        return {"message": f"delete todo task: {index} successfully."}

    # FIXME: http_put 的请求总是提示 content Field required，修改成 post 就正常了！这是 bug 吗？
    @http_post("/{index}", response=generic_response, summary="改 - 指定索引的待办事项")
    def update_todo(self, request: HttpRequest, index: int, content: Form[str]):
        self._check_index(index)

        db.lset(self.TODO_LIST_KEY, index, content)
        return {"message": f"update todo task: {index} successfully."}

    @http_get("/{index}", response=generic_response, summary="查 - 指定索引的待办事项")
    def get_todo(self, request: HttpRequest, index: int):
        self._check_index(index)
        data = db.lrange(self.TODO_LIST_KEY, index, index)
        return {"data": data[0].decode("utf-8")}


@api_controller("/redis/todolist/v2", tags=router.tags)
class TodoListV2Controller:
    pass


def redis_register_controllers(api):
    api.register_controllers(
        TodoListController,
        QuickNoteController
    )

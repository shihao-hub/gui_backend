import functools
import re
from typing import List

from bson import ObjectId

from django.http import HttpRequest
from ninja import Router, Form, Query
from ninja_extra import api_controller, http_get, http_post, http_put, http_delete

from apps.api.exceptions import BadRequestError
from apps.api.settings import mongodb_db as db
from apps.api.schemasets.mongodb import TodoListItemRequestSchema, TodoListItemResponseSchema
from apps.api.shared.utils import generic_response
from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

log = Log()

router = Router(tags=["mongodb"])

# mongodb 数据库有问题... 但是写快速的小项目似乎方便很多？将 mongodb 视为什么比较好？集合+字典序列？json 数据存储+搜索引擎？

TODOLIST_COLLECTION_NAME = "todolist"


@router.get("/todolist/list", response=List[TodoListItemResponseSchema])
def todolist_list(request: HttpRequest):
    co = db.get_collection(TODOLIST_COLLECTION_NAME)

    return list(co.find())  # find() 返回值是个 cursor


@router.post("/todolist")
def todolist_create(request: HttpRequest, data: TodoListItemRequestSchema = Form()):
    co = db.get_collection(TODOLIST_COLLECTION_NAME)

    # NOTE:
    #   增 - 创建的时候用 str(ObjectId()) 创建！！！
    inserted_data = {
        "_id": str(ObjectId()),
        **data.dict()
    }

    co.insert_one(inserted_data)
    return inserted_data


@router.delete("/todolist", response=generic_response)
def todolist_delete(request: HttpRequest, unique_id: str = Query(alias="_id")):
    co = db.get_collection(TODOLIST_COLLECTION_NAME)

    res = co.delete_one({"_id": unique_id})
    if res.deleted_count == 0:
        raise BadRequestError(f"_id={unique_id} 不存在，删除失败")
    return {"message": f"删除 {unique_id} 成功"}


@router.post("/todolist/update", response=generic_response)
def todolist_update(request: HttpRequest,
                    unique_id: str = Query(alias="_id"),
                    data: TodoListItemRequestSchema = Form()):
    co = db.get_collection(TODOLIST_COLLECTION_NAME)

    updated_data = data.dict()

    res = co.update_one({"_id": unique_id}, {"$set": updated_data})
    if res.modified_count == 0:
        return 400, {"message": f"_id={unique_id} 不存在，更新失败"}
    return {"message": f"更新 {unique_id} 成功"}


@router.get("/todolist", response=TodoListItemResponseSchema)
def todolist_retrieve(request: HttpRequest, unique_id: str = Query(alias="_id")):
    co = db.get_collection(TODOLIST_COLLECTION_NAME)
    data = co.find_one({"_id": unique_id})
    if data is None:
        raise BadRequestError(f"_id={unique_id} 不存在")
    return data

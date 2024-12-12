from typing import List, Dict

import requests

from django.http import HttpRequest, StreamingHttpResponse
from ninja import Router, Form

from apps.api.shared.utils import generic_response, get_registered_router
from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

log = Log()

router = Router(tags=["chatgpt"])


@knowledge("EventStream", "requests.post")
def get_ai_event_steam_response(message: List[Dict]):
    url = "https://aliyun.zaiwen.top/admin/chatbot"
    data = {
        "message": message,
        "mode": "gpt4_o_mini",
        "prompt_id": "",
        "key": None
    }

    def event_stream():
        with requests.post(url, json=data, stream=True, timeout=15) as response:
            for line in response.iter_lines():
                if line:
                    yield line.decode("utf-8") + "\n"

    # 2024-12-13-00:10：测试发现，没什么问题。但是前端没有建立 EventStream，Swagger UI 本身无法连接到 SSE！
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"  # 关闭缓存
    return response


@router.post("/ask_ai_one_question", summary="问 ai 一个问题")
def ask_ai_one_question(request: HttpRequest, prompt: str = Form(max_length=100)):
    message = [
        {
            "role": "user",
            "content": prompt,
        }
    ]
    return get_ai_event_steam_response(message)


@router.post("/ask_english_ai", summary="英语学习 ai")
def ask_english_ai(request: HttpRequest, prompt: str = Form(max_length=100)):
    init_prompt = """
    在接下来的对话中，你要帮助我学习英语。因为我的英语水平有限，所以拼写可能会不准确，如果语句不通顺，请猜测我要表达的意思。在之后的对话中，除了正常理解并回复我的问题以外，还要指出我说的英文中的语法错误和拼写错误。
    并且在以后的对话中都要按照以下格式回复:
    （翻译）此处将英文翻译成中文
    （回复）此处写你的正常回复
    （勘误）此处写我说的英文中的语法错误和拼写错误，如果夹杂汉字，请告诉我它的英文
    （提示）如果有更好或更加礼貌的英文表达方式，在此处告诉我如果你能明白并能够照做
    请说“我明白了”
    """
    # 使用经典同步
    message = [
        {
            "role": "user",
            "content": init_prompt
        },
        {
            "role": "assistant",
            "content": "我明白了。"

        },
        {
            "role": "user",
            "content": prompt,
        }
    ]

    return get_ai_event_steam_response(message)

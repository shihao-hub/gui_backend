from typing import List, Dict

import requests
from pydantic import HttpUrl

from django.http import HttpRequest, StreamingHttpResponse
from ninja import Router, Form

from apps.api.shared.utils import generic_response, get_registered_router
from apps.core.shared.log import Log
from apps.core.shared.utils import knowledge

log = Log()

router = Router(tags=["chatgpt"])


# TODO: 如何实现命令行 + EventStream？浏览器太卡了。
#   简单设想：
#       python 程序，argparse 库，while 循环等待用户输入，一个消息列表存储所有问答记住上下文来调用 ai 接口。
#       注意，argparse 似乎有更好的替代品。pyinstaller 似乎不太好用？

@knowledge("EventStream", "requests.post", "proxies=proxies, verify=False")
def _get_ai_event_steam_response(message: List[Dict]):
    url = "https://aliyun.zaiwen.top/admin/chatbot"
    data = {
        "message": message,
        "mode": "gpt4_o_mini",
        "prompt_id": "",
        "key": None
    }

    # proxies = {
    #     "http": "http://proxy:port",
    #     "https": "http://proxy:port",
    # }
    proxies = None

    def event_stream():

        try:
            # TODO: 如何不设置 verify=False 而是使用证书认证访问 https 呢？
            # 2024-12-14：这个 event_stream 要求 timeout 似乎需要设置大一点？
            with requests.post(url, json=data, stream=True, timeout=300, proxies=proxies, verify=False) as response:
                for line in response.iter_lines():
                    if line:
                        yield line.decode("utf-8") + "\n"
        except Exception as e:
            # TODO: 这样治标不治本，比如说，返回值还是 200！
            log.error(str(e))
            yield f"Error: {e}\n"

    # 2024-12-13-00:10：测试发现，没什么问题。但是前端没有建立 EventStream，Swagger UI 本身无法连接到 SSE！
    event_stream_generator = event_stream()
    response = StreamingHttpResponse(event_stream_generator, content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"  # 关闭缓存
    return response


@router.post("/ask_ai_one_question", summary="问 ai 一个问题")
def ask_ai_one_question(request: HttpRequest, prompt: str = Form(max_length=1000)):
    message = [
        {
            "role": "user",
            "content": prompt,
        }
    ]
    return _get_ai_event_steam_response(message)


@router.post("/summarize_text", summary="ai 总结")
def summarize_text(request: HttpRequest, prompt: Form[str]):
    # TODO: 找到更优的 prompt
    #   题外话，这个可以帮我直接总结一篇英文文章，这样可以先看他的总结然后看英文，岂不是更方便？
    #   就像阅读代码一样，以后让 ai 帮我们生成注释（之前刷到的幽灵注释比较好...为什么 idea 不支持？）
    message = [
        {
            "role": "user",
            "content": "请帮我将下面的内容总结一下\n\n" + prompt,
        }
    ]
    return _get_ai_event_steam_response(message)


@router.post("/ask_english_ai", summary="问 英语学习 ai")
def ask_english_ai(request: HttpRequest, prompt: str = Form(max_length=1000)):
    init_prompt = """
    在接下来的对话中，你要帮助我学习英语。因为我的英语水平有限，所以拼写可能会不准确，如果语句不通顺，请猜测我要表达的意思。在之后的对话中，除了正常理解并回复我的问题以外，还要指出我说的英文中的语法错误和拼写错误。
    并且在以后的对话中都要按照以下格式回复:
    【翻译】此处将英文翻译成中文
    【回复】此处写你的正常回复
    【勘误】此处写我说的英文中的语法错误和拼写错误，如果夹杂汉字，请告诉我它的英文
    【提示】如果有更好或更加礼貌的英文表达方式，在此处告诉我如果你能明白并能够照做
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

    try:
        log.info(f"123")

        return _get_ai_event_steam_response(message)
    except Exception as e:
        log.error(f"ask_english_ai error: {e}", print_stack=True)


@router.post("/ask_function_naming_ai", summary="问 函数命名 ai")
def ask_function_naming_ai(request: HttpRequest, prompt: str = Form(max_length=100)):
    prompt_format = """
        我有一个功能为：{prompt} 的函数，请帮我命名。
        要求：你的回复只能是一个 json 列表，使用蛇形命名法（markdown 的相关内容也不需要）
    """
    prompt = prompt_format.format(prompt=prompt)
    message = [
        {
            "role": "user",
            "content": prompt,
        }
    ]
    return _get_ai_event_steam_response(message)


@router.post("/summarize_url_content", response=generic_response, summary="ai 总结网址信息")
def summarize_url_content(request: HttpRequest, url: Form[HttpUrl]):
    # TODO: 很多网站都需要登录怎么解决？
    #   有些网站没关系：https://www.ruanyifeng.com/blog、https://www.codedump.info 等
    #       国外好多网站不需要登录！
    # TODO: 将 get 到的 html 中文文本抽出来
    #   2024-12-14-173427.md
    #   涉及爬虫技术 -> requests, lxml, Beautiful Soup, Scrapy, Selenium, Pandas, Puppeteer, Requests-HTML,
    response = requests.get(url, verify=False)
    content = response.content.decode("utf-8")
    log.info(content)
    message = [
        {
            "role": "user",
            # TODO: 找到更优的 prompt
            "content": "请帮我将下面的文章内容总结一下\n\n" + content,
        }
    ]
    return _get_ai_event_steam_response(message)

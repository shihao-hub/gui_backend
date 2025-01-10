"""
### 面向过程思路
1. 接收用户输入
2. 判断输入是否为指令，
   如果是命令，则处理命令；
   如果不是命令，则调用 gpt 接口，返回结果

#### 流程图


### 简单建模思路
首先进行需求分析:
- 支持用户循环输入问题，调用 gpt 接口，然后返回结果
- 支持用户输入指令，如 "/save" 保存当前对话，"/exit" 退出程序
然后进行建模：
- 定义一个类 ChatBot，包含一个列表 `messages` 用于存储用户和 gpt 的对话记录
- 定义一些类 Command、Invoker、Receiver 等，运用设计模式之命令模式
"""
import logging
import time
import warnings
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Dict, Tuple, Union, List

import requests
from loguru import logger as log

# log.add("file.log", rotation="10 MB")  # 自动轮换日志文件
warnings.filterwarnings("ignore")  # 忽略所有的警告信息，包括未来警告、弃用警告等

# constants
MESSAGES_MAX_SIZE = 30

AI_API_STRUCT = namedtuple("AI_API_STRUCT", ["URL", "MODE", "PROMPTR_ID", "KEY", ])(**dict(
    URL="https://aliyun.zaiwen.top/admin/chatbot",
    MODE="gpt4_o_mini",
    PROMPTR_ID="",
    KEY=None
))

# settings: switches
settings = namedtuple("settings", ["SIMULATE_TYPEWRITER_EFFECT", "MULTI_LINE_INPUT", "PRINT_IN_ONE_BREATH"])(**dict(
    SIMULATE_TYPEWRITER_EFFECT=False,
    MULTI_LINE_INPUT=True,
    PRINT_IN_ONE_BREATH=False  # 太慢了
))

# NOTE: 当你发现某件事情比较麻烦的时候，可以去找一下第三方库
# log = logging.getLogger(__name__)

console_log = print

# module shared
messages = []


# -------------------------------------------------------------------------------------------------------------------- #
class Command(ABC):

    @abstractmethod
    def execute(self, params: Union[Tuple, List] = None, named_params: Dict = None):
        pass


class SaveCommand(Command):
    """
    保存某次回答，-1 表示上一次，-2 表示倒数第二次，以此类推
    > 注意，index 支持正数和负数
    """

    def _write_file(self, content: str):
        this = self

        filename = f"./resources/ag2/{time.strftime('%Y-%m-%d-%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()

    def execute(self, params: Union[Tuple, List] = None, named_params: Dict = None):
        params = params if params else None
        if params is None:
            index = -1
        else:
            index = int(params[0])

            # 1,1-1 | 2,3-1 | 3,5-1 | 4,7-1 | 5,9-1 ... ==> n,2*n-1-1
            # -1,-1 | -2,-3 | -3,-5 | -4,-7 | -5,-9 ... ==> n,2*n+1

            if index < 0:
                index = 2 * index + 1
            else:
                index = 2 * index - 1

            # print("Test:", "{old_index}, {index}".format(old_index=params[0], index=index))

        try:
            answer = messages[index].get("content")
            question = messages[index - 1].get("content")
            self._write_file(f"## {question}\n\n{answer}")
            print("Saved file success!")
        except IndexError:
            print(f"Index overflow, excepted [0, {len(messages)}) or ({-(len(messages))}, -1]")


def process_command(command: str):
    words = command.strip().split(" ")
    command_map = {
        "save": SaveCommand
    }
    cls = command_map.get(words[0])
    if cls is None:
        print(f"Unknown command: {command}, expected: {(', '.join(command_map.keys()))}")
        return
    command_obj = cls()
    command_obj.execute(words[1:])


# -------------------------------------------------------------------------------------------------------------------- #

def _generate_prompt(raw_question: str):
    return raw_question


def _attempt_to_clear_messages():
    if len(messages) > MESSAGES_MAX_SIZE:
        messages.clear()


def _generate_request_data():
    return {
        "message": messages,
        "mode": AI_API_STRUCT.MODE,
        "prompt_id": AI_API_STRUCT.PROMPTR_ID,
        "key": AI_API_STRUCT.KEY
    }


def _get_and_print_response_content(response):
    content = []

    for line in response.iter_lines():
        if line is None:
            continue

        output = line.decode("utf-8")
        content.append(output)

        if settings.PRINT_IN_ONE_BREATH:
            continue

        if settings.SIMULATE_TYPEWRITER_EFFECT:
            for e in output:
                time.sleep(0.02)
                print(e, end="", flush=True)
            print()
        else:
            print(output)

    res = "\n".join(content)
    if settings.PRINT_IN_ONE_BREATH:
        print(res, flush=True)

    return res


def invoke_ai_api(question: str):
    _attempt_to_clear_messages()

    messages.append({
        "role": "user",
        "content": _generate_prompt(question)
    })

    print(f"{AI_API_STRUCT.MODE} 回复：", end="", flush=True)
    response = requests.post(AI_API_STRUCT.URL, json=_generate_request_data(), stream=True, verify=False)

    messages.append({
        "role": "assistant",
        "content": _get_and_print_response_content(response)
    })
    print()


# -------------------------------------------------------------------------------------------------------------------- #
def __get_multi_line_input_mode_2():
    lines = []
    line = input()
    while line.strip() != "@end":
        lines.append(line)
        line = input()
    return "\n".join(lines)


def _get_multi_line_input():
    # 退而求其次，遇到空行就执行，这导致需要按两次回车...
    lines = []
    while True:
        line = input()

        if line.strip() == "@begin":
            return __get_multi_line_input_mode_2()

        # 2024-16-00:30：优化，每次提问前面的空行都忽略（使用的时候发现的，由此可见，测试的重要性）
        if line == "" and not lines:
            continue

        # print(ord('\r'), ord('\n')) # 13 10
        # print([ord(e) for e in line]) # 会忽略 \r \n，即获取不到
        if line == "":
            break  # 如果输入为空行，则退出循环
        lines.append(line)
    return "\n".join(lines)


def get_user_input():
    if settings.MULTI_LINE_INPUT:
        user_input = _get_multi_line_input()
    else:
        user_input = input()
    return user_input.strip()


# -------------------------------------------------------------------------------------------------------------------- #

def main():
    while True:
        user_input = get_user_input()

        if user_input.startswith("/"):
            process_command(user_input[1:])
            continue

        invoke_ai_api(user_input)


if __name__ == '__main__':
    main()

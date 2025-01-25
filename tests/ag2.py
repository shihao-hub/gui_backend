"""
### 面向过程思路
1. 接收用户输入
2. 判断输入是否为指令，
   如果是命令，则处理命令；
   如果不是命令，则调用 gpt 接口，返回结果

#### 流程图（不一定是最新的或者完全正确的）
flowchart TD
    A[开始] --> B{判断首行是否为空}
    B -->|是| A
    B -->|否| C{判断首行是否为 @cmd}
    C -->|是| D[解析并执行命令]
    D --> E[继续循环]
    C -->|否| F{判断首行是否为 @begin}
    F -->|是| G{判断模式}
    G -->|默认模式| H[获取用户输入]
    G -->|英语学习模式| I[获取用户输入并调用 ask_english_ai]
    F -->|否| J[获取用户输入]
    H --> K[调用 invoke_ai_api]
    I --> L[调用 ask_english_ai]
    J --> M[调用 invoke_ai_api]
    K --> E
    L --> E
    M -

### 简单建模思路
首先进行需求分析:
- 支持用户循环输入问题，调用 gpt 接口，然后返回结果
- 支持用户输入指令，如 "/save" 保存当前对话，"/exit" 退出程序
然后进行建模：
- 定义一个类 ChatBot，包含一个列表 `messages` 用于存储用户和 gpt 的对话记录
- 定义一些类 Command、Invoker、Receiver 等，运用设计模式之命令模式

### 项目总结:2025-01-11
1. 项目实战是需要根据需求来实战才是有价值的、有意义的。  <br>
   拿到一个需求后，通过可行性分析、需求分析、概要设计等流程输出相关文档，  <br>
   然后才进入开发阶段，开发完成之后还需要测试等流程，最终才能上线。  <br>
2. 通过重构 ag.py 简单训练了一些能力：
   - 需求分析能力
   - 建模能力
   - 代码能力
   - 重构和设计模式运用能力
   - 自测能力
   等，虽然只是简单训练，但是我认为是有意义的。
3. 在重构 ag.py 的过程中，我体会到，工作是枯燥的，需求是频繁的，大部分需求都不是困难的，而是琐碎的。  <br>
   编码能力不是算法解题能力，**人无法想象不存在的事物，或者说大部分人只能理解我们经历过的事物**，这意味着
   编码能力的提升不是空谈也不是空想，而是需要大量变成练习的。虽然大部分内容很枯燥，但是实际上这和应试教育
   区别不大，能力的提升就是困难的，学习也就是痛苦的事情！  <br>
4. 从 2024-03-25 到 2025-01-11，不到一年的时间，我已经稍微理解了**技术不是主要的**这句话的意义了：
   - 大部分程序员的工作就是和业务打交道
   - 大部分程序的工作是劳动密集型工作
   - 大部分程序的工作是容易被替代的，只需要熟练度足够，任何人都能替代和编码相关的你的作用，除非你有其他特别之处
5. 从现在开始，我需要在学习技术（道）的过程中，穿插学习术这种内功！增加自己的不可替代性，向架构师等方向尝试努力。  <br>
   当然，工作之处，技术是重要的，至少学习两三年，做到能快速掌握一门新技术即可（大部分新技术并不需要学术知识，就是你的编程熟练度）  <br>
> 工作是枯燥的，学习是痛苦的，加油吧，漫漫长路。  <br>
> 不知道合适我再回顾上面的总结时，我会说，我当时的思想太浅了，太稚嫩了。希望两个月我就做做到这个程度！

> to be continue ...
"""
import json
import platform
import os
import re
import time
import traceback
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
settings = namedtuple("settings", ["SIMULATE_TYPEWRITER_EFFECT", "PRINT_IN_ONE_BREATH"])(**dict(
    SIMULATE_TYPEWRITER_EFFECT=False,
    PRINT_IN_ONE_BREATH=False  # 太慢了
))

# NOTE: 当你发现某件事情比较麻烦的时候，可以去找一下第三方库
# log = logging.getLogger(__name__)


console_log = print

# module shared
messages = []

# -------------------------------------------------------------------------------------------------------------------- #
KEY_WORDS = (
    "@cmd",
    "@begin",  # Question: 此处的 @begin、@end 就是为了获取多行输入，这个命名是否不太合适？
    "@end",

    "@begin:ask_english_ai",
    "@begin:-aea",
)


class Command(ABC):

    @abstractmethod
    def execute(self, params: Union[Tuple, List] = None, named_params: Dict = None):
        pass


class SaveCommand(Command):
    """
        保存某次回答，-1 表示上一次，-2 表示倒数第二次，以此类推
        > 注意，index 支持正数和负数

        Usage:
        @cmd save [index] [name]
    """

    @staticmethod
    def create_directory(self, dir_path: str):
        raise NotImplemented

    # ---------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def __handle_base_filename(base_filename: str):
        base_filename_no_suffix, file_suffix = os.path.splitext(base_filename)
        if not file_suffix:
            file_suffix = ".md"

        # 去掉所有特殊字符
        base_filename_no_suffix = re.sub(r"[\\/:*?\"<>|\s]", "", base_filename_no_suffix)

        # 最大长度为 255 个字符
        res = base_filename_no_suffix + file_suffix
        return res[:255]

    @staticmethod
    def write_file(content: str, base_filename: str = None):

        use_makedirs_function = False

        if base_filename is None:
            base_filename = f"{time.strftime('%Y-%m-%d-%H%M%S')}.md"
        else:
            # Notice, when we use the staticmethod of SaveCommand,
            # we need to consider the consequences when we alter the name of the SaveCommand class.
            base_filename = SaveCommand.__handle_base_filename(base_filename)

        dirs = ["resources", "ag2"]
        dir_path = "./" + "/".join(dirs) + "/"

        if use_makedirs_function:
            os.makedirs(dir_path, exist_ok=True)
        else:
            tmp_dir_path = "./"
            for dirname in dirs:
                tmp_dir_path = tmp_dir_path + dirname + "/"
                if not os.path.exists(tmp_dir_path):
                    os.mkdir(tmp_dir_path)

        filename = os.path.join(dir_path, base_filename)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()

    def execute(self, params: Union[Tuple, List] = None, named_params: Dict = None):
        # params = params if params else None
        saved_file_basename = None

        # params would be None, [], or (), so we need use it with `if not params`.
        if not params:
            index = -1
        else:
            # Question:
            #   Whether I need to check the type of params?
            #   If someone uses the command such as `@cmd save abc`, this would cause a crash.
            index = int(params[0])

            # 1,1-1 | 2,3-1 | 3,5-1 | 4,7-1 | 5,9-1 ... ==> n,2*n-1-1
            # -1,-1 | -2,-3 | -3,-5 | -4,-7 | -5,-9 ... ==> n,2*n+1

            index = (2 * index + 1) if index < 0 else (2 * index - 1)

            # print("Test:", "{old_index}, {index}".format(old_index=params[0], index=index))

            if len(params) == 2:
                saved_file_basename = params[1]

        try:
            assert len(messages) % 2 == 0, "The length of `messages` field must be even."
            answer = messages[index].get("content")
            question = messages[index - 1].get("content")
            question = "\n".join(["> " + e + "  " for e in question.split("\n")])
            # 6*\n
            # <==>
            # > title \n -> because the `"\n".join` function does not append a newline after the last element.
            # \n -> `>` need have a newline with other element.
            # \n
            # \n -> markdown newline
            # \n
            # \n -> markdown newline
            self.write_file(f"{question}\n\n\n\n\n\n{answer}", base_filename=saved_file_basename)
            print("Saved file success!")
        except IndexError:
            print(f"Index overflow, excepted [0, {len(messages)}) or ({-(len(messages))}, -1]")

    # ---------------------------------------------------------------------------------------------------------------- #


class SaveAllCommand(Command):

    def execute(self, params: Union[Tuple, List] = None, named_params: Dict = None):
        res = []

        assert len(messages) % 2 == 0, "The length of `messages` field must be even."
        i = 0
        while i < len(messages):
            raw_question = messages[i].get("content")
            question = "\n".join(["> " + e + "  " for e in raw_question.split("\n")])
            answer = messages[i + 1].get("content")
            res.append(f"{question}\n\n\n\n{answer}\n\n\n")
            i += 2

        SaveCommand.write_file("\n".join(res))
        print("Saved all files success!")


class HelpCommand(Command):
    # NOTE: 2025-01-11
    #   实战使用 Command, HelpCommand, SaveCommand 似乎体会到了开闭原则的力量，只需要创建新类即可！
    #   虽然我的逻辑中还得修改函数内容，但是实际上可以变成配置文件，然后通过配置文件来动态加载命令，从而真正实现开闭原则。
    def execute(self, params: Union[Tuple, List] = None, named_params: Dict = None):
        if not params:
            print("Usage:\n"
                  "    @cmd help list_keywords")
            return

        if params[0] == "list_keywords":
            print("Keywords:\n", "\n".join(KEY_WORDS))


# NOTE: 此处有一些影子：通过配置动态注入命令，只需要创建新类，并修改这个配置即可，不必修改 process_command 函数的逻辑！
COMMAND_MAP = {
    "save": SaveCommand,
    "saveall": SaveAllCommand,
    "help": HelpCommand,
}


def process_command(command: str):
    # The Command is split by the blank character. Such as: lua.exe sum.lua 1 2 3 4 5 <==> sum(...) -> 15
    words = command.strip().split(" ")

    # convert `words` into parameters and named parameters.
    params = []
    named_params = {}

    # NOTE: 此处的实现不知道是否合理，但是我有一点可以明确，那就是测试的重要性，只要软件质量得以满足，那就是好代码！
    #   软件质量：可靠性、可维护性、可移植性等
    i = 1
    while i < len(words):
        word = words[i]
        if word.startswith("--"):
            try:
                named_params[word[2:]] = words[i + 1]
            except IndexError:
                print(f"Invalid command: `{command}`")
                return
            i += 1
        else:
            params.append(word)
        i += 1
    # `@cmd save -1 name --filename name --index -1` -> `['-1', 'f'] {'filename': 'name', 'index': '-1'}`
    # print(params, named_params)

    cls = COMMAND_MAP.get(words[0])
    if cls is None:
        print(f"Unknown command: {command}, expected: {(', '.join(COMMAND_MAP.keys()))}")
        return
    command_obj = cls()
    command_obj.execute(params, named_params)


# -------------------------------------------------------------------------------------------------------------------- #

def _generate_prompt(raw_question: str):
    return raw_question


def __persist_messages():
    filename = f"./ag2_{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(messages, ensure_ascii=False))
    # log.info("Persisting messages success!")


def _attempt_to_clear_messages():
    if len(messages) >= MESSAGES_MAX_SIZE:
        __persist_messages()
        messages.clear()


def _generate_request_data(message):
    return {
        "message": message,
        "mode": AI_API_STRUCT.MODE,
        "prompt_id": AI_API_STRUCT.PROMPTR_ID,
        "key": AI_API_STRUCT.KEY
    }


def _print_and_get_response_content(response, get=True):
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

    if get:
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
    response = requests.post(AI_API_STRUCT.URL, json=_generate_request_data(messages), stream=True, verify=False)

    messages.append({
        "role": "assistant",
        "content": _print_and_get_response_content(response)
    })
    print()


def ask_english_ai(prompt: str):
    init_prompt = """
        在接下来的对话中，你要帮助我学习英语。因为我的英语水平有限，所以拼写可能会不准确，如果语句不通顺，请猜测我要表达的意思。在之后的对话中，除了正常理解并回复我的问题以外，还要指出我说的英文中的语法错误和拼写错误。
        并且在以后的对话中都要按照以下格式回复:
        【翻译】此处将英文翻译成中文
        【回复】此处写你的正常回复
        【勘误】此处写我说的英文中的语法错误和拼写错误，如果夹杂汉字，请告诉我它的英文
        【提示】如果有更好或更加礼貌的英文表达方式，在此处告诉我如果你能明白并能够照做
        请说“我明白了”
    """
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
    print(f"{AI_API_STRUCT.MODE} 回复：", flush=True)
    response = requests.post(AI_API_STRUCT.URL, json=_generate_request_data(message), stream=True, verify=False)
    _print_and_get_response_content(response, get=False)


# -------------------------------------------------------------------------------------------------------------------- #
def __get_multi_line_input_mode_2():
    lines = []
    line = input()
    while line.strip() != "@end":
        lines.append(line)
        line = input()
    return "\n".join(lines)


def _get_multi_line_input(first_line):
    # 退而求其次，遇到空行就执行，这导致需要按两次回车...
    lines = []
    line = first_line
    while True:
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
        line = input()
    return "\n".join(lines)


def get_user_input(first_line):
    return _get_multi_line_input(first_line)


# -------------------------------------------------------------------------------------------------------------------- #
def system_pause():
    if platform.system() == "Windows":
        # os.system("pause")  # Windows 系统
        input("按回车键继续...")
    else:
        input("按回车键继续...")  # Linux 或 macOS 系统


# -------------------------------------------------------------------------------------------------------------------- #
def get_first_non_empty_line():
    first_line = input()
    while first_line == "":
        first_line = input()
    return first_line


def main():
    # main 是主函数，main 用到的函数我认为可以不加 _，因为 _ 实在太丑了。当然，如果在类中，那最好还是加吧。

    # TODO: 组合函数模式 + SLAP

    while True:
        # Adding try-except expression to catch any exceptions, so that the program can continue running.
        # In addition, this method can also record the error message.
        try:
            answer_pattern = "default"

            first_line = get_first_non_empty_line()
            striped_first_line = first_line.strip()

            # check/inspect if it is a matching keyword
            if striped_first_line.startswith("@"):
                keyword = striped_first_line.split(" ")[0]
                if keyword not in KEY_WORDS:
                    print(f"Unknown keyword: `{keyword}`, expected {', '.join(KEY_WORDS)}")
                    continue

            # if it is a `@cmd` keyword, process the command and continue
            if striped_first_line.startswith("@cmd"):
                command = striped_first_line[4:].strip()
                process_command(command)
                continue

            # other special processing based on `@begin`
            if striped_first_line.startswith("@begin"):
                if striped_first_line != "@begin":
                    pattern = striped_first_line[len("@begin") + 1:]
                    if pattern in ["ask_english_ai", "-aea"]:
                        answer_pattern = "ask_english_ai"
                        first_line = "@begin"
                    else:
                        print(f"Unknown keyword: `{striped_first_line}`.")
                        continue

            user_input = get_user_input(first_line)

            if answer_pattern == "default":
                invoke_ai_api(user_input)
            elif answer_pattern == "ask_english_ai":
                ask_english_ai(user_input)
        except Exception as e:
            log.error(f"{e}\n{traceback.format_exc()}")
            # system_pause()

            # If some exceptions occur, I need to clear the `messages` field,
            # so that I can start a new conversation next time.
            # The reason why I do it like this is that I mush promise/ensure the length of messages is even.
            print("Clearing message cache was successful! Let us start a new conversation!")
            messages.clear()


if __name__ == '__main__':
    main()

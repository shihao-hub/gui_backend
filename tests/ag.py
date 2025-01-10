# TODO: 如何实现命令行 + EventStream？浏览器太卡了。
#   简单设想：
#       python 程序，argparse 库，while 循环等待用户输入，一个消息列表存储所有问答记住上下文来调用 ai 接口。
#       注意，argparse 似乎有更好的替代品。pyinstaller 似乎不太好用？


import argparse
import datetime
import functools
import inspect
import os.path
import re
import sys
import subprocess
import threading
import time
import warnings
from typing import List, Dict, TypeVar, Generic, Callable

import requests

warnings.filterwarnings("ignore")  # 忽略所有的警告信息，包括未来警告、弃用警告等

# -------------------------------------------------------------------------------------------------------------------- #
# shared
# -------------------------------------------------------------------------------------------------------------------- #
T = TypeVar("T")


class CommandControllerMessageException(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data


class OutputParameter(Generic[T]):
    """ 输出参数类，当然，这是违背《重构》这本书的理念的，该书不建议使用输出参数 """

    def __init__(self, value: T = None):
        # init 的参数 value: T 不会让代码分析工具误解吗？但是 Optional[T] 也会误解吧？
        # 目前来说，没发现什么问题，确实方便了许多，之后再看吧！
        self._value: T = value

    def set_value(self, value: T):
        self._value = value

    def get_value(self) -> T:
        return self._value

    def __str__(self):
        return str(self._value)


# -------------------------------------------------------------------------------------------------------------------- #
# EnableVoiceFunctionObject
# -------------------------------------------------------------------------------------------------------------------- #
class EnableVoiceFunctionObject:
    def __init__(self, gpt_url):
        self.gpt_url = gpt_url

    @staticmethod
    def convert_audio_to_text(filename, file):
        url = "http://localhost:8888/api/tool/convert_audio_to_text"
        files = {
            "audio": (filename, file)  # 指定文件名和文件对象
        }
        response = requests.post(url, files=files)
        # TODO: 校验是否出错
        if response.status_code != 200:
            print(f"\r{response}")
            # TODO: 如果是 json 格式，否则打印其他的
            print(f"\r{response.json()}")
            raise Exception("读取录音功能执行出错！")
        return response.json().get("data")

    def record(self, output: OutputParameter):
        output.set_value("默认提示词")

        thread_id = threading.current_thread().ident

        # 启动录音功能，注意此处是阻塞在这里的
        print(f"\rThread-{thread_id}: 启动录音子进程")
        result = subprocess.run(["./dist/recording.exe"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)  # capture_output=True

        print(f"\rThread-{thread_id}: 录音子进程执行完毕，执行语音识别逻辑")
        # print("stdout:", result.stdout)
        # print("stderr:", result.stderr)

        # TODO: 读取录音内容：识别的程度还不够...
        # TODO: 优化使用，用户至少需要知道什么时候开始的...比如声音...
        filepath = "resources/media/recording.wav"
        with open(filepath, "rb") as file:
            filename = os.path.basename(filepath)
            output.set_value(self.convert_audio_to_text(filename, file))

    def run(self) -> str:
        print("已开启录音功能")  # 输入 end 即可结束录音

        output = OutputParameter("")

        print(f"执行录音进程，生成 prompt 中，请等待...")

        # 刚刚崩溃了发现，还是线程好啊！崩溃了没事！
        thread = threading.Thread(target=self.record, args=(output,))
        thread.start()

        # 为什么执行此处时，线程没有执行？注释掉才正常
        #   难道是 input io 中断了？-> 大概率是的！整个进程中断了！
        # while input() != "end":
        #     print("已开启录音功能，输入 end 即可结束录音")
        # 终止录音进程，生成 prompt

        # 循环输出 \/ 生成加载图标
        def show_loading_animation(condition: Callable = None):
            if condition is None:
                condition = lambda: True  # NOQA
            spinner = ("|", "/", "-", "\\",)
            idx = 0
            while condition():
                # TODO: 应该使用 \b 退格的方式实现？-> 《流畅的 Python》
                #   之所以这样考虑，是因为其他线程打印 print 的时候会导致我的这里没有清空（但是好像无法实现吧？）
                # sys.stdout.write(f"\b{spinner[idx]}")
                sys.stdout.write(f"\r{spinner[idx]} Loading...")
                sys.stdout.flush()
                idx = (idx + 1) % len(spinner)
                time.sleep(0.1)

        loading_thread = threading.Thread(target=show_loading_animation, args=(lambda: thread.is_alive(),))
        loading_thread.start()
        loading_thread.join()

        # TOD~O: 添加 tqdm 库的加载功能？或者是《流畅的 Python》中实现的命令行加载显示
        #   注意，此处如果开个新线程的话，需要通过 event 的方式终止线程
        #   已完成
        thread.join()
        print("\r线程执行完毕，返回 prompt")

        return output.get_value()


# -------------------------------------------------------------------------------------------------------------------- #
# CommandController
# -------------------------------------------------------------------------------------------------------------------- #
class CommandController:
    CMD_FLAG = "@cmd"

    def __init__(self, messages):
        self.messages = messages

    def _is_valid_command(self, command: str):
        this = self

        return command.startswith(self.CMD_FLAG)

    def _is_defined_command(self, command: str):
        this = self
        # TODO: 能不能避免数据冗余？
        #   题外话，多看源码？后面重点放在 Java 上最后肯定能好好提升 Python 能力的。编程是互通的。
        return command in [
            "save_last_answer",
            "-sla",
            "save_all",  # TODO: 注册功能
        ]

    def parse(self, command: str):
        if not self._is_valid_command(command):
            # 如果用户请求不是命令，那么此处还可以做一些事情...
            # 比如，--stream 1/--stream 0 的方式可以决定 gpt 的输入是流式还是非流式
            try:
                pattern = re.compile(r"--([a-zA-Z_]+)\s+(\d+)\s?$")  # --a-zA-z_ number（这样最省事，而且还能实现功能，多方便）
                for matcher in pattern.finditer(command):
                    # print(matcher)  # 此处体现了 log.debug 和 log.info 的用处了... gpt 的回答需要显示，其余一切不应该显示在看着他
                    pass
            except Exception as e:
                e = e
                pass
            return
        command = command[len(self.CMD_FLAG):].strip()
        if not self._is_defined_command(command):
            raise CommandControllerMessageException(f"@cmd {command} 未定义！")
        # TODO: 命令行的智能提示功能是如何实现的？比如 python manager.py shell...
        # TODO: 这些命令感觉可以生成配置，运行时就能变化...
        if command in ["save_last_answer", "-sla"]:
            target_path = "./resources"
            if not os.path.exists(target_path):
                os.mkdir(target_path)
            cur_time = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            # TODO: 让 self.messages 更健壮一点
            #   简单构想：
            #       messages List[Dict] 的 Dict 中存在属性 role，从后往前找，通过 role = assistant/user 确定问题和答案

            # 此处保存的时候，是不是还得转义一下文件名呢？要是不符合 os 的命名规则怎么办？
            # 测试的重要性！... 一个人怎么做得到这些！除了天才...
            # 解决了：不需要用问题做文件名，毕竟问题很多
            filename = os.path.join(target_path, f"{cur_time}.md")
            # TODO: 有没有一种可能，用一个专门管理文件上传的进程，类似 mysql、redis 这样，管理我的文件呢？
            #   尤其上次刷到个抖音，部署我们自己的知识库（当然 gpt 的答案仅供参考），知识库 + 文件管理系统，协同服务多好？
            #   顺便联想一下，linux 的 | 管道符，也是为了进程协同！
            #   题外话，（个人而言）
            #       Python -> 快速 Web 原型开发/小型 Web 开发、数据分析、图像处理、语音识别、人工智能（NumPy、Pandas、TensorFlow、PyTorch等）
            #       Java -> 至少 0.5、1、1.5 年的工作语言（提升自己的编程能力、阅读源码能力、需求分析能力、TDD等整体能力）
            #       HTML/CSS/JS -> 写个人网站的工具、单线程语言和异步技术
            #       C/C++/Lua -> 数据结构（目前来说，偏学术吧...）
            #       Rust? -> 未来再说，应该是和 C/C++ 一个地位
            #       SQL、Linux
            #       Ruby? -> Ruby 可以作为高效的脚本语言来处理日常的系统管理任务，例如文件操作、数据库维护、自动化测试等。 or 《MongoDB 实战》？
            #       Go? -> 优先级最低
            #       C#? -> 游戏相关
            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"提问：{self.messages[-2].get("content")}\n\n\n\n")
                file.write(self.messages[-1].get("content"))
                file.flush()

            raise CommandControllerMessageException("保存上一次的回答成功！")
        elif command == "save_all":
            # FIXME: 目前假设 user 和 assistant 是轮着来的，而且先 user 后 assistant
            target_path = "./resources"
            if not os.path.exists(target_path):
                os.mkdir(target_path)
            cur_time = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            filename = os.path.join(target_path, f"{cur_time}.md")
            file = open(filename, "w", encoding="utf-8")
            for i in range(0, len(self.messages) - 1, 2):
                user = self.messages[i].get("content")
                assistant = self.messages[i + 1].get("content")
                file.write(f"## {user}\n\n")
                file.write(f"{assistant}\n\n")
            file.flush()
            file.close()
            raise CommandControllerMessageException("保存所有回答成功！")


# -------------------------------------------------------------------------------------------------------------------- #
# other
# -------------------------------------------------------------------------------------------------------------------- #
class GPTMessage:
    def __init__(self, data: List):
        self._data = data

    def get_data(self):
        return self._data

    def set_data(self, value):
        # TODO: 这算什么？self._data 是引用啊，这个结构也不算好吧？
        #   js 的 get set 类似 lua table 的 __index __newindex 这样的功能，此处算啥？不是最佳实践，不好用。
        self._data.append(value)


# -------------------------------------------------------------------------------------------------------------------- #
# 函数入口
# -------------------------------------------------------------------------------------------------------------------- #
def main():
    # TODO: messages 可以封装成类，getter 和 setter 的存在可以让我做一些处理，比如 messages 长度较长时，切断
    messages: List[Dict] = []
    url = "https://aliyun.zaiwen.top/admin/chatbot"
    data = {
        "message": messages,
        "mode": "gpt4_o_mini",
        "prompt_id": "",
        "key": None
    }
    command_controller = CommandController(messages)

    while True:
        # flag:
        upload_image = False

        # 为什么老旧电脑要配一个 RESET 按钮？

        # pycharm run 无法终止输入...
        # 如果你希望从标准输入中读取所有行，直到输入结束，可以使用 sys.stdin
        # lines = sys.stdin.read().strip().splitlines()
        # prompt = "\n".join(lines)

        # (N)!: 不论代码如何，只要能保证需求满足、测试全面就是好代码（当然，这只是好代码的最低标准，即可靠性和准确性）
        #   除此以外，可扩展性、可读性等也都是重点！

        # TO~DO: 实现粘贴进来多行效果 -> 已解决。但是需要按两次回车
        # prompt = input()

        # TODO: 我的剪切板复制了一张图片，我如何在命令行按 ctrl+v 的时候将其上传？
        #   简单设想：
        #       始终监听用户的键盘事件，监听到 ctrl+v 时，如果是图片，就将其上传。命令行实现这个好困难...
        #       要不继续退而求其次？（虽然我这样确实不太好，感觉像半吊子，但是第一版，实现了就行了呗？...）
        #           @cmd ask_ai_and_attach_one_image -ask_and_one_img
        #           监听键盘事件，按下 ctrl+v 的时候判断是否是图片。如果不是则循环交互响应。
        #           如果图片成功保存，则打印：请输入你的问题，然后等待用户输入（这里好像有 goto 就好了哈哈）
        #           用户输入自然视其为纯粹的输入... 然后问问题即可！（zaiwen 也提供了上传图片的功能）
        #       我又想到了，直接类似 linux 那些不就行了？
        #       make -nB （见图片 make.png）代表详细展示这个 makefile 文件的命令
        #       那我 @cmd -nB 是不是可以代表其他的，比如指定 image 所在的目录？这样的话我为什么要实现上面说的那些情况呢？
        #       又或者，假如问答的末尾有 @cmd 呢？又比如类似 cursor、codegeex 一样，开头有 @image 呢？
        #       又或者，@question 后的内容才是你的提问呢？
        #       退而求其次，以 @[a-zA-Z_] 为分隔符（假如问题里面存在 @xxx 就惨了...），拆出所有命令序列（此处好像需要正则表达式的力量？）
        #           gcc
        #               -c
        #               -o ./xxx/x.c
        #               -march=i386
        #               -fno-pic
        #               -DAR_H="arch/x.h"
        #               -fcf-protection=none
        #       TODO: 解决问题里面存在 @xxx 的问题，还是说直接不识别？需要你转移？\@ 才是 @？ -> 问问 gpt

        # 退而求其次，遇到空行就执行，这导致需要按两次回车...
        lines = []
        while True:
            line = input()
            # 2024-16-00:30：优化，每次提问前面的空行都忽略（使用的时候发现的，由此可见，测试的重要性）
            if line == "" and not lines:
                continue

            # print(ord('\r'), ord('\n')) # 13 10
            # print([ord(e) for e in line]) # 会忽略 \r \n，即获取不到
            if line == "":
                break  # 如果输入为空行，则退出循环
            lines.append(line)
        prompt = "\n".join(lines)

        # print("Paste your text (Press Ctrl+D or Ctrl+Z and Enter to finish):")
        # prompt = sys.stdin.read()

        if prompt.startswith("@cmd") and prompt[4:].strip() in ["enable_voice_function", "-evf"]:
            prompt = EnableVoiceFunctionObject(url).run()
        else:
            # TODO: 这里的结构太丑陋了，没办法优化吗？尤其这个命令功能、录音功能，能模块化多好，但是最佳实践是什么呢？
            #   而且这里的结构显然是有问题的，目前进入此处则意味着做的事情和问 ai 问题无关了。
            # 添加命令功能
            try:
                command_controller.parse(prompt)
            except CommandControllerMessageException as e:
                print(f"{e}\n")
                continue
            except Exception as e:
                print(f"发生错误 -> {e.__class__}: {e}\n")  # 发生异常时，打印信息，进入下一次循环
                continue

        # 注意，主循环不必 try except，崩溃了那就应该崩溃
        print("提问：" + prompt)

        def check_messages_size_and_clear():
            # size = sys.getsizeof(messages)
            # print("------", size)
            # 我选择单纯判断长度，暂且设置成 30 吧
            if len(messages) > 30:
                messages.clear()

        check_messages_size_and_clear()

        messages.append({
            "role": "user",
            "content": prompt
        })
        with requests.post(url, json=data, stream=True, verify=False) as response:
            print(f"{data.get('mode')} 回复：", end="")
            content = []
            for line in response.iter_lines():
                if line:
                    output = line.decode("utf-8")
                    content.append(output)
                    # 模拟一个字一个字吐出
                    for e in output:
                        time.sleep(0.02)  # 模拟打字机效果
                        print(e, end="", flush=True)
                    print()
            messages.append({
                "role": "assistant",
                "content": "\n".join(content)
            })
            print()


if __name__ == '__main__':
    main()

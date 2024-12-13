# TODO: 如何实现命令行 + EventStream？浏览器太卡了。
#   简单设想：
#       python 程序，argparse 库，while 循环等待用户输入，一个消息列表存储所有问答记住上下文来调用 ai 接口。
#       注意，argparse 似乎有更好的替代品。pyinstaller 似乎不太好用？


import argparse
import sys
import time
import warnings
from typing import List, Dict

import requests

warnings.filterwarnings("ignore")  # 忽略所有的警告信息，包括未来警告、弃用警告等


def main():
    messages: List[Dict] = []
    url = "https://aliyun.zaiwen.top/admin/chatbot"
    data = {
        "message": messages,
        "mode": "gpt4_o_mini",
        "prompt_id": "",
        "key": None
    }
    while True:
        # 为什么老旧电脑要配一个 RESET 按钮？

        # pycharm run 无法终止输入...
        # 如果你希望从标准输入中读取所有行，直到输入结束，可以使用 sys.stdin
        # lines = sys.stdin.read().strip().splitlines()
        # prompt = "\n".join(lines)

        # TODO: 实现粘贴进来多行效果
        prompt = input()
        print("提问：" + prompt)
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
            print("")


if __name__ == '__main__':
    main()

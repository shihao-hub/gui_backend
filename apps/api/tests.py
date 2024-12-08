import asyncio
import json
import pprint
import unittest

import aiohttp
import requests


class SimpleTestCase:  # (unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_main(self):
        this = self
        pass


def test_a():
    url = "https://aliyun.zaiwen.top/admin/chatbot"
    data = {
        "message": [
            {
                "role": "user",
                "content": " sudo apt install silversearcher-ag"
            },
            {
                "role": "assistant",
                "content": "`silversearcher-ag`，通常称为 **The Silver Searcher**，是一个快速的文本搜索工具，类似于 `grep`，但性能更优，特别是在大规模代码库中非常有效。它非常适合开发者使用，因为它能够快速查找文件中的文本。\n\n如果您希望在基于 Debian 的系统（例如 Ubuntu）上安装 The Silver Searcher，可以使用以下命令：\n\n```bash\nsudo apt update\nsudo apt install silversearcher-ag\n```\n\n### 命令解释：\n- `sudo`: 以超级用户权限执行命令。\n- `apt`: 是 Debian/Ubuntu 系统包管理工具。\n- `update`: 更新本地的包索引，使其与远程仓库同步。\n- `install`: 安装指定的软件包。\n- `silversearcher-ag`: 是您要安装的具体软件包名称。\n\n### 安装后的使用\n\n安装完成后，您可以通过在命令行中使用 `ag` 命令来运行 The Silver Searcher。例如：\n\n```bash\nag \"要搜索的文本\" 路径\n```\n\n### 一些示例：\n\n1. **在当前目录及其子目录中搜索文本**：\n   ```bash\n   ag \"hello\"\n   ```\n\n2. **在特定文件类型中搜索**：\n   ```bash\n   ag --java \"someMethodName\"  # 在 `.java` 文件中搜索\n   ```\n\n3. **限制搜索深度**：\n   ```bash\n   ag --depth 2 \"search term\"\n   ```\n\n4. **显示行号和匹配的文件**：\n   ```bash\n   ag -n \"search term\"\n   ```\n\n### 额外功能\n\n- **支持正则表达式**：`ag` 支持 Perl 兼容的正则表达式，您可以使用更复杂的搜索模式。\n\n- **排除特定目录和文件**：您可以通过 `--ignore` 选项来排除某些目录或文件，例如：\n  ```bash\n  ag --ignore-dir=vendor \"search term\"\n  ```\n\nThe Silver Searcher 是一个非常强大的工具，它的速度和功能使其在开发和代码搜索中非常受欢迎。安装后可以根据需要查看 **man** 手册或 `--help` 来获得更多使用选项。"
            },
            {
                "role": "user",
                "content": "帮我回答",
                "assets": [
                    "6adbbb30-7082-4330-8494-06859fe311c0"
                ]
            },
            {
                "role": "assistant",
                "content": "遇到“Segmentation Fault”的问题通常是由于程序试图访问未被允许的内存区域。以下是一些常见的排查步骤，帮助你定位和解决问题：\n\n1. **检查指针**：确保所有指针在使用前已经正确初始化，并且指向有效的内存地址。\n\n2. **数组越界**：检查数组的访问，确保没有越界访问的情况。\n\n3. **内存分配**：如果你的程序中使用了动态内存分配（如`malloc`、`calloc`等），确保每次分配后都进行了正确的检查，并且在使用后释放内存。\n\n4. **调试工具**：使用调试工具（如`gdb`）逐步执行程序，查看在哪一行代码出现了错误。可以通过命令 `run` 启动程序，出现错误时使用 `backtrace` 查看调用栈。\n\n5. **打印日志**：在关键位置添加打印语句，帮助追踪程序的执行流程，确定问题发生的地方。\n\n6. **查阅文档**：如果使用了库函数，确保按照文档正确使用，检查参数及返回值。\n\n7. **简化代码**：如果问题难以定位，尝试简化代码，逐步注释掉部分代码，找出导致错误的最小代码片段。\n\n通过以上步骤，应该能帮助你找到并解决“Segmentation Fault”的问题。如果仍有困难，可以将相关代码和错误信息贴出来，以便进一步分析。"
            },
            {
                "role": "user",
                "content": "这张图片能不能用前端技术实现出来？",
                "assets": [
                    "ae879e1d-4381-499e-82c7-168010e02c8b"
                ]
            }
        ],
        "mode": "gpt4_o_mini",
        "prompt_id": "",
        "key": None
    }
    with requests.post(url, json=data, stream=True) as response:
        for line in response.iter_lines():
            if line:
                print(line.decode("utf-8"))


def test_b():
    url = "https://aliyun.zaiwen.top/admin/chatbot"
    data = {
        "message": [
            {
                "role": "user",
                "content": "我需要实现一个函数，他个功能是调用 ai 获得某种函数的命名，请帮我给这个函数命名一下。返回的答案的 json 的列表，不要有其他内容（我也不需要 markdown 的内容）",
            }
        ],
        "mode": "gpt4_o_mini",
        "prompt_id": "",
        "key": None
    }

    res = []

    async def fetch_event_stream():
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                async for line in response.content:
                    if line:
                        res.append(line.decode("utf-8"))
                        # print(line.decode("utf-8"))

    # 运行异步任务
    asyncio.run(fetch_event_stream())
    print(pprint.pformat(json.loads("".join(res))))


if __name__ == '__main__':
    pass
    # unittest.main()
    # test_a()
    test_b()

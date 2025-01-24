"""
### Tips
1. F13 到 F15 是历史遗留的键位，几乎没有实际用途。


"""
import ast
import configparser
import datetime
import functools
import time
import traceback
from collections import namedtuple
from io import StringIO

import numpy as np
import pyautogui
from loguru import logger as log  # This library can change the color of characters in the command line.


# TODO: python 内置 .ini 配置文件解析类？
# TODO: 前置操作处理


class GetSettingsInitParamsHelper:
    def __init__(self):
        pass

    def get_params_from_config(self, config: configparser.ConfigParser):
        this = self

        HOURS = ast.literal_eval(config.get("settings", "HOURS"))
        SLEEP_INTERVAL = int(config.get("settings", "SLEEP_INTERVAL"))


def get_settings_init_params(field_names):
    def get_params_from_config(config: configparser.ConfigParser):

        HOURS = ast.literal_eval(config.get("settings", "HOURS"))
        SLEEP_INTERVAL = int(config.get("settings", "SLEEP_INTERVAL"))

    helper = GetSettingsInitParamsHelper()

    # attention: 此处看似有大量重复代码，但是这里也恰恰表现出：
    #   先尝试执行某个操作，如果出错再捕获异常 这个方法存在的一些问题。（Easier to Ask for Forgiveness than Permission）
    #       《重构》作者更推崇 LBYL（Look Before You Leap）风格，即先检查，再执行。
    #   在执行某个操作之前先进行检查，以确定操作是否安全。这种风格在某些情况下可以更具可读性，（Look Before You Leap）
    #       但在 Python 文化中，EAFP 方式更为常见，尤其是在处理可能失败的操作时。
    #       在 Python 和其他动态类型语言中，EAFP 风格通常更受欢迎，因为它使代码更加简洁，并且将错误处理的逻辑放在异常处理块中，通常比在每一步之前都进行检查要清晰。
    #   - **EAFP** (Easier to Ask for Forgiveness than Permission) - 先尝试执行，然后通过捕获异常来处理错误。
    #   - **LBYL** (Look Before You Leap) - 在执行之前先进行条件判断。

    try:
        # updating the configuration uses the data from the `config.ini`.

        # Please use utf-8 encoding, otherwise it will be garbled.
        # Because the configparser library may perform encoding inference(编码推导).
        # If the ini file has a chinese character, the default encoding will be deduced to(被推导成) gbk.
        config = configparser.ConfigParser()
        config.read("./config.ini", encoding="utf-8")
        # question: 不存在这个文件理当报错啊！为什么不报错？

        # FIXME: ugly code!!!
        res = dict(
            HOURS=ast.literal_eval(config.get("settings", "HOURS")),
            SLEEP_INTERVAL=int(config.get("settings", "SLEEP_INTERVAL"))
        )
    except Exception as exception:
        sio = StringIO()  # `StringIO` is a file-like object. Please use string directly.
        sio.write("""
        [settings]
        HOURS = 2
        SLEEP_INTERVAL = 180
        """)

        # default
        log.warning(f"读取配置信息失败，将使用默认配置。失败原因：{exception}")

        config = configparser.ConfigParser()
        config.read_string(sio.getvalue())

        res = dict(
            HOURS=ast.literal_eval(config.get("settings", "HOURS")),
            SLEEP_INTERVAL=int(config.get("settings", "SLEEP_INTERVAL"))
        )

        sio.close()

    for key in np.setdiff1d(field_names, list(res.keys())):
        res.pop(key)

    return res


settings_field_names = ["HOURS", "SLEEP_INTERVAL"]
settings = namedtuple("settings", settings_field_names)(**get_settings_init_params(settings_field_names))

TIMEOUT_INTERVAL = 60 * 60 * settings.HOURS
START_TIME = time.time()

mut_count = 0


def on_press_f15():
    global mut_count
    mut_count += 1
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{now} -> 第 {mut_count} 次按压 f15 键")


def check_timeout():
    if time.time() - START_TIME > TIMEOUT_INTERVAL:
        raise EOFError(f"{settings.HOURS} 小时到了，进程终止")


def system_pause():
    # because the `input` function doesn't have a buffer,
    # this means that the print speed of stderr is slower than that.
    # so, there is a delay.
    time.sleep(0.1)
    input("输入任意键结束\n")


def main_exception_handler_decorator(func):
    @functools.wraps(func)
    def wrapper():
        try:
            func()
        except Exception as e:
            log.error(f"{e}\n{traceback.format_exc()}")
            system_pause()

    return wrapper


@main_exception_handler_decorator
def main():
    while True:
        check_timeout()

        pyautogui.press("f15")
        on_press_f15()

        pyautogui.sleep(settings.SLEEP_INTERVAL)


if __name__ == '__main__':
    main()

"""
    实现周期性移动鼠标以避免睡眠，键盘按下 Ctrl + C 终止进程
    但是有点丑陋...
"""
import collections
import datetime
import time
import uuid

import pyautogui as auto

# pyinstaller -F scripts\projects\click_screen_timer.ini.py

# setting
setting = collections.namedtuple(f"setting_{str(uuid.uuid4()).replace('-', '')}", [
    "condition_1"
])(**dict(
    # struct
    condition_1={"on": False, "value": auto.Point(951, 775)}  # 点击位置修改，当 WeLink 放在中央的时候，保证 WeLink 始终在最上层
))

# const
TIME_INTERVAL = 300
TIMEOUT = 60 * 60 * 2
left_position, right_position = auto.Point(100, 400), auto.Point(1800, 400)

# mut
count = 0

if setting.condition_1["on"]:
    left_position = setting.condition_1["value"]

max_time = time.time() + TIMEOUT
while time.time() < max_time:
    # 这里要注意不要点到关闭窗口等

    # 记录当前鼠标所在位置，之后移动回来
    old_point = auto.position()
    # 点击左上角
    left_upper_point = auto.Point(3, 0)
    auto.click(*left_upper_point)
    # 移动回原来的位置
    auto.moveTo(*old_point)

    count += 1
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{now} -> 第 {count - 1} 次点击屏幕或移动鼠标 (interval: {TIME_INTERVAL} s)")

    auto.sleep(TIME_INTERVAL)
print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -> 超时终止 (timeout: {TIMEOUT} s)")

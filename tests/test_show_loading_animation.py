import sys
import time
from typing import Callable


def show_loading_animation(condition: Callable = None):
    condition = condition() if condition else True
    spinner = ("|", "/", "-", "\\",)
    idx = 0
    while condition:
        sys.stdout.write(f"\r{spinner[idx]} Loading...")
        sys.stdout.flush()
        idx = (idx + 1) % len(spinner)
        time.sleep(0.1)


if __name__ == '__main__':
    show_loading_animation(lambda: True)

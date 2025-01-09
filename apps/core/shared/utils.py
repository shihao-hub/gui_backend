import functools
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar, Generic, Tuple, Union

from apps.api.settings import redis_db as db
from apps.api.settings import rq_queue
from apps.core.shared.log import Log

T = TypeVar("T")
E = TypeVar("E")
log = Log()


class OK(Generic[T, E]):
    def __init__(self, value: T):
        self._value = value

    def value(self) -> T:
        return self._value


class Err(Generic[T, E]):
    def __init__(self, error: E):
        self._error = error

    def error(self) -> E:
        return self._error


Result = Union[OK[T, E], Err[T, E]]


# 一个函数来演示如何使用 Result
# def divide(a: float, b: float) -> Result[float, str]:
#     if b == 0:
#         return Err("Cannot divide by zero")
#     return OK(a / b)
#
#
# # 使用示例
# result = divide(10, 2)
# if isinstance(result, OK):
#     print(f"Result: {result.value()}")
# else:
#     print(f"Error: {result.error()}")
# result = divide(10, 0)
# if isinstance(result, OK):
#     print(f"Result: {result.value()}")
# else:
#     print(f"Error: {result.error()}")


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


# with ThreadPoolExecutor(max_workers=1) as pool:
#   pool.submit(thread_fn)


def save_knowledge(key, knowledge_list):
    try:
        if rq_queue:
            log.info("开始执行 rq 异步队列任务")
        else:
            # log.warning("异步任务改同步任务。原因：windows 环境下无法使用 rq，请使用 linux 环境或者 docker。")
            pass

        db.sadd(key, *knowledge_list)
        db.expire(key, 60)  # 保证始终最新？
        # TODO: 异步任务队列，用来生成报告
        # django 项目启动后是否存在监听器呢？可能那样收集一下，来生成最新报告
    except Exception as e:
        log.error(f"{e}", print_stack=True)


def knowledge(*knowledge_list: *Tuple[str, ...]):
    # TODO: 目前只是充当注释，后续此处可以统计一个知识库。（比如，存储整个函数的源代码）
    #   **func_name - func_no - func_location**
    #   - knowledge1
    #   - knowledge2
    #   - knowledge3
    def outer(func):
        # (N)!: 注意，rq enqueue 函数的 *args, **kwargs 似乎无法传递 function，不知道是本就不支持还是什么意思？
        key = f"knowledge:{func.__module__}.{func.__qualname__}"
        if rq_queue:
            rq_queue.enqueue(save_knowledge, key, knowledge_list)
        else:
            save_knowledge(key, knowledge_list)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return outer

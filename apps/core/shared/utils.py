import functools
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

from apps.api.settings import redis_db as db
from apps.api.settings import rq_queue
from apps.core.shared.log import Log

log = Log()


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
    # TODO: 目前只是充当注释，后续此处可以统计一个知识库。
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

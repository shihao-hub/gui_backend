"""
## [深入理解 Python 协程：原理、用法与实战](https://weiwang123.blog.csdn.net/article/details/144332595)
Python 的协程（Coroutine）是一种强大的并发编程工具，能让你以非阻塞方式处理 I/O 密集型任务、异步操作等场景。

### 1 什么是协程？
协程是比线程更轻量的并发单元，其核心特性是 协作式调度。传统线程依赖操作系统的抢占式调度，而协程通过显式地让出控制权（await）实现并发。

|  特性   |  线程   | 协程    |
| --- | --- | --- |
|  调度方式   |  抢占式调度   |  协作式调度   |
|  开销   |   需要操作系统线程资源  |  轻量级，无需 OS 参与   |
|  执行方式   |  并行   |  并发   |
|   适用场景  |  	CPU 密集型任务   |  I/O 密集型任务   |

---

### 2 协程的基础概念
#### 2.1 可等待对象

#### 2.2 async 和 await

---

### 3 greenlet 的核心概念
greenlet 是一个轻量级的协程库，可以用来管理协程的上下文切换。相比于 Python 的原生 asyncio，greenlet 更贴近底层，但也更灵活。  <br>
greenlet 提供了用户态协程的实现。它允许程序在不同的任务间显式切换，而不依赖事件循环。  <br>

**核心操作**
- 创建协程: 使用 greenlet.greenlet 创建协程对象。
- 显式切换: 使用 greenlet.switch() 在协程之间切换。

#### 3.1 基本用法
以下是一个使用 greenlet 的简单示例：
```python
    from greenlet import greenlet

    def task1():
        print("Task 1: Start")
        gr2.switch()  # 切换到 task2
        print("Task 1: Resume")
        gr2.switch()  # 再次切换到 task2
        print("Task 1: End")

    def task2():
        print("Task 2: Start")
        gr1.switch()  # 切换到 task1
        print("Task 2: Resume")
        gr1.switch()  # 再次切换到 task1
        print("Task 2: End")

    # 创建两个 greenlet 协程
    gr1 = greenlet(task1)
    gr2 = greenlet(task2)

    # 启动协程 task1
    gr1.switch()
```
输出：
```
Task 1: Start
Task 2: Start
Task 1: Resume
Task 2: Resume
Task 1: End
Task 2: End
```
解释：
- gr1.switch() 激活 task1，并在 task1 中切换到 task2。
- gr2.switch() 激活 task2，再切回 task1。


#### 3.4 总结greenlet
Python 的协程提供了强大的异步编程支持，从底层的 greenlet 到高级的 asyncio，适合不同场景的需求。在实际开发中：
- 简单场景: 使用 asyncio 提供的 async/await。
- 性能优化: 在特定场景下可尝试 greenlet。
- 调试和维护: 始终保持协程代码简洁，并善用调试工具。
---

### 4. gevent 的核心概念
gevent 是基于 greenlet 的高级协程库，为 Python 提供了更简单易用的异步编程方式。
它通过 绿色线程（green thread） 和 猴子补丁（monkey patching） 实现自动化的协程切换，在网络和 I/O 密集型场景中表现出色。

#### 4.5 gevent 的优缺点
优点：
1. 简单易用: 自动调度，无需显式 await。
2. 高性能: 基于 greenlet，切换速度快，开销低。
3. 自动非阻塞: 通过猴子补丁自动将阻塞操作变为非阻塞。
4. 生态丰富: 支持队列、池化等常见并发场景。
缺点：
1. 强依赖猴子补丁: 部分标准库或第三方库可能与补丁冲突。
2. 单线程: 与 asyncio 类似，无法利用多核 CPU。
3. 调试复杂: 异步切换的时序问题可能导致调试困难。

> to be continue...
"""
import time

from greenlet import greenlet


def test_a():
    def task1():
        print("Task 1: Start")
        gr2.switch()  # 切换到 task2
        print("Task 1: Resume")
        gr2.switch()  # 再次切换到 task2
        print("Task 1: End")

    def task2():
        print("Task 2: Start")
        gr1.switch()  # 切换到 task1
        print("Task 2: Resume")
        gr1.switch()  # 再次切换到 task1
        print("Task 2: End")

    # 创建两个 greenlet 协程
    gr1 = greenlet(task1)
    gr2 = greenlet(task2)

    # 启动协程 task1
    gr1.switch()


def test_producer_and_consumer():
    def producer():
        for i in range(5):
            print(f"Producing item {i}")
            consumer_gr.switch(i)  # 将生产的物品传递给消费者

    def consumer():
        while True:
            item = producer_gr.switch()  # 接收生产者的物品
            print(f"Consuming item {item}")

    producer_gr = greenlet(producer)
    consumer_gr = greenlet(consumer)

    # 启动消费者（消费者会切换到生产者）
    consumer_gr.switch()


class CoroutineScheduler:
    """ 可以通过一个调度器管理多个 greenlet 协程，从而实现简单的任务调度。 """

    def __init__(self):
        self._tasks = set()
        self._scheduler_gr = None

    def add_task(self, task):
        self._tasks.add(task)

    def add_tasks(self, tasks):
        for task in tasks:
            self.add_task(task)

    def switch(self):
        if self._scheduler_gr is None:
            raise RuntimeError("IllegalCallerException")
        self._scheduler_gr.switch()

    def run(self):
        def scheduler():
            # while True 应该永不终止
            while True:
                for task in self._tasks:
                    if not task.dead:
                        task.switch()
                    else:
                        self._tasks.remove(task)

                time.sleep(0.1)  # 模拟调度器的调度间隔

        self._scheduler_gr = greenlet(scheduler)  # 创建调度器
        self._scheduler_gr.switch()  # 启动调度器


# !!!
def test_scheduler():
    """ 协程调度器 """

    manager = CoroutineScheduler()

    scheduler_gr = manager

    # scheduler_gr 共享管理空间，或者也可以理解为事件循环主线程
    def task1():
        for i in range(3):
            print(f"Task 1: {i}")
            scheduler_gr.switch()  # 切换回调度器

    def task2():
        for i in range(3):
            print(f"Task 2: {i}")
            scheduler_gr.switch()  # 切换回调度器

    def scheduler():
        # while True 应该永不终止
        while True:
            all_dead = True  # 假设所有任务都已完成
            for task in tasks:
                if not task.dead:  # 检查任务是否完成
                    all_dead = False  # 如果有任务未完成，标记为 False
                    task.switch()  # 切换到任务

            if all_dead:  # 如果所有任务都已完成，退出循环
                print("All tasks completed.")
                break

            time.sleep(0.1)  # 模拟调度器的调度间隔

    # 创建任务
    task1_gr = greenlet(task1)
    task2_gr = greenlet(task2)
    tasks = [task1_gr, task2_gr]

    # 创建调度器
    scheduler_gr = greenlet(scheduler)
    # 启动调度器
    scheduler_gr.switch()

    # manager.add_tasks(tasks)
    # manager.run()


def test_gevent_spawn():
    import time

    import gevent
    from gevent import monkey

    """
       猴子补丁：自动让阻塞方法变为异步  <br>
       猴子补丁是 gevent 的一大特色。通过 gevent.monkey.patch_all()，gevent 会自动替换标准库中的阻塞方法，如 socket、time.sleep 等，使它们变为异步操作。  <br>
       - time.sleep
       - requests
    """
    monkey.patch_all()

    class TaskParamDataObject:
        def __init__(self, name, delay):
            self.name = name
            self.delay = delay

    def task(name: str, delay: int, task_param: TaskParamDataObject):
        print(f"{task_param.name} started")
        time.sleep(task_param.delay)
        # gevent.sleep(task_param.delay)  # 模拟耗时任务，每次循环后让出控制权
        print(f"{task_param.name} ended, the sleeping time is {task_param.delay:.3f}s")

    # 创建并启动绿色线程，等待所有线程完成
    gevent.joinall([
        gevent.spawn(task, f"Task{i}", 0.1 * i, TaskParamDataObject(f"Task{i}", 0.1 * i))
        for i in range(1, 11)
    ])


def test_web_page_capture():
    import warnings

    from gevent import monkey

    warnings.filterwarnings("ignore")

    monkey.patch_all()  # 打补丁，支持异步 I/O

    import gevent
    import requests

    def fetch(url):
        print(f"Fetching: {url}")
        response = requests.get(url, verify=False)  # 非阻塞请求
        print(f"Done: {url}, Status: {response.status_code}")

    urls = [
        "https://www.python.org",
        "https://www.python.org",
        # "https://www.github.com",
    ]

    gevent.joinall([gevent.spawn(fetch, url) for url in urls])


def test_gevent_queue():
    import gevent
    import gevent.exceptions
    from gevent.queue import Queue

    # 创建一个共享队列
    queue = Queue()

    def producer():
        for i in range(5):
            print(f"Producing {i}")
            queue.put(i)
            gevent.sleep(1)  # 模拟生产过程
        # while True:
        #     pass

    def consumer():
        while True:
            item = queue.get()  # 从队列中取出数据
            print(f"Consuming {item}")
            gevent.sleep(0.5)  # 模拟消费过程
            # try:
            #     item = queue.get()  # 从队列中取出数据
            #     print(f"Consuming {item}")
            #     gevent.sleep(0.5)  # 模拟消费过程
            # except gevent.exceptions.LoopExit:
            #     pass

    gevent.joinall([
        gevent.spawn(producer),
        gevent.spawn(consumer),
    ])


if __name__ == '__main__':
    # test_a()
    # test_producer_and_consumer()
    test_scheduler()
    # test_gevent_spawn()
    # test_web_page_capture()
    # test_gevent_queue()
    pass

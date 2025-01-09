-[x] 123
-[ ] 456
-[ ] 789

---

| 特性   | 线程         | 协程           |
|------|------------|--------------|
| 调度方式 | 抢占式调度      | 协作式调度        |
| 开销   | 需要操作系统线程资源 | 轻量级，无需 OS 参与 |
| 执行方式 | 并行         | 并发           |
| 适用场景 | 	CPU 密集型任务 | I/O 密集型任务    |

---

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

### 2 协程的基础概念
#### 2.1 可等待对象

#### 2.2 async 和 await

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

> to be continue...

---

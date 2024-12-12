import os
import sys

import redis

from django.conf import settings

RESOURCES = settings.BASE_DIR / "apps/api/resources"

# redis connect/db 0
redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

# -------------------------------------------------------------------------------------------------------------------- #
# Redis Queue
# -------------------------------------------------------------------------------------------------------------------- #
# RQ 是一个简单的 Python 库，可以将任务放入 Redis 队列并异步处理。它设计简单，便于使用，适合中小型项目。
# - 简单易用、直接使用 Redis 作为后端、基础功能优秀，适合快速实现

# RQ（Redis Queue），人如其名，用 redis 做的队列任务
# redis ，众所周知， 它的列表可以做队列，rq就是把job放进队列里，然后启worker挨个做完
# 另外rq极其简单，官方文档短小精悍，容易上手

# 使用方法：job = rq_queue.enqueue(fn, *args, **kwargs)
if sys.platform != "win32":
    import rq

    rq_queue = rq.Queue(connection=redis.StrictRedis(host="localhost", port=6379, db=15))
else:
    rq_queue = None

# -------------------------------------------------------------------------------------------------------------------- #
# Celery
# -------------------------------------------------------------------------------------------------------------------- #
# Celery 是 Python 中最流行的异步任务队列库，支持多种消息代理（Broker），如 RabbitMQ、Redis 等。
# 它非常适合需要执行长时间运行任务的应用程序，并提供了丰富的功能，如结果存储、任务调度、重试机制等。
# - 支持任务调度、任务重试机制、结果存储支持、大量社区支持和文档

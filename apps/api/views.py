__all__ = ["api"]

# views.py 文件目前可以视其为 django 的入口文件，虽然其实主要是在 urls.py 导入了，所以算入口文件。其他文件也行的吧！

from apps.api.shared.singleton import Singleton

api = Singleton.api

# 将所有代码引入进来 (Q)!: 为什么不会出现循环引用的情况？A: 模块以延迟加载的方式导入（但是，出现循环引用显然代码结构有问题啊...)
from apps.api import exceptionsets  # NOQA

# 有没有更好的办法？
from apps.api import viewsets  # NOQA

# 2024-12-09：
# 找到更好的办法了！ninja 文档里的 router，可以类似 django 的 include 的自动引入
# ninja router 使用案例：
#   api = NinjaAPI()
#   api.add_router("", "apps.api.viewsets.index_views.router")
#   api.add_router("/tools", "apps.api.viewsets.tools_views.router")
#   api.add_router("/tasks", "apps.api.viewsets.tasks_views.router")
#   api.add_router("/redis", "apps.api.viewsets.redis_views.router")
#   api.add_router("/chatgpt", "apps.api.viewsets.chatgpt_views.router")
#   api.add_router("/async", "apps.api.viewsets.async_views.router")

# 不行 -> ImportError: Module "apps.api.viewsets.tools_views" does not define a "router" attribute/class
# from apps.api.viewsets.tools_views import router as tools_router
# api.add_router("/tools", tools_router)
# 上面这样可以，但是 -> AttributeError: 'Router' object has no attribute 'register_controllers'

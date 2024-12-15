from django.contrib import admin
from django.urls import path, include

from apps.index.views import TodoListView, QuickNoteView

urlpatterns = [
    # TODO: 首页的主要作用是跳转过去！需要设置一个简陋的主页，类似 windows 的大图标模式，一行三个
    #   当然最好还有 tags 设置，就够了！首页就充当一个入口即可！
    #   参考：
    #   - 搜索 123：https://sousuo123.com/
    #   - 波特工具站：https://tool.butof.com/
    path("quicknote", QuickNoteView.as_view()),
    path("todolist", TodoListView.as_view())
]

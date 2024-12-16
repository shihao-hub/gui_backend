from pathlib import Path

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView


# NOTE:
#   测试发现，django-allauth 多半是个远古库。或者是国外用的。反正我这边用不了。

class TodoListView(TemplateView):
    template_name = str(Path("todolist/todolist.html"))


class QuickNoteView(TemplateView):
    template_name = str(Path("quicknote/quicknote.html"))

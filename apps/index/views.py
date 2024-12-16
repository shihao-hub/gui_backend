from pathlib import Path

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView


class TodoListView(TemplateView):
    template_name = str(Path("todolist/todolist.html"))


class QuickNoteView(TemplateView):
    template_name = str(Path("quicknote/quicknote.html"))

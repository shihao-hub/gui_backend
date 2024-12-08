__all__ = ["api"]

from apps.api.shared.singleton import Singleton

api = Singleton.api

# 将 viewsets 中的所有代码引入进来
from apps.api import viewsets  # NOQA

# 2024-12-10：
# from apps.api.testsets import exercises_tests
# 不行，python manager.py test apps.api 不会执行 exercises_tests 中的代码！
# viewsets 内为什么可以呢？导入的时候不都是将包中代码执行一遍吗？
# from apps.api.testsets.exercises_tests import *
# 问了 gpt：Django 默认使用 unittest 测试框架，这要求测试文件名应以 test_ 开头，比如 test_exercise.py。解决了！！！

from apps.api.testsets import test_exercise

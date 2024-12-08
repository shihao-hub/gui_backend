# 创建该目录的目的是，将 django app 的 tests 文件充当直接测试的入口
#   但是发现，直接运行 tests.py 文件时，工作目录就是 tests.py 所在目录，因此找不到 apps 包
#   所以还是只在 tests.py 文件里测试吧（可以用 python 自带的 TestCase，不用 Django 的 TestCase

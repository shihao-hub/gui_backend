from abc import ABC, abstractmethod


class Mixin1(ABC):
    @abstractmethod
    def mixin1_method(self):
        pass


class Mixin2Base:
    def __init__(self, *args):
        print("Mixin2Base.__init__", *args)


class Mixin2(Mixin2Base):
    def mixin2_method(self):
        print("Mixin2 method")


class Person:
    def __init__(self, name):
        self.name = name
        print(f"Person initialized with name: {self.name}")


"""
这样的话，直接 super 调用的就是 Person！

当然，如果混入类没定义 __init__，Mixin 放前面也没事！

但是放后面可以类比 Java 接口欸？
而且还有好处！Mixin 如果继承了其他类怎么办？放在前面会导致执行 Mixin 的 `__init__` 函数！

但是这又有个问题，混入类有 `__init__` 函数有什么意义？显然混入类不允许有 `__init__` 啊！
放在后面的话，哪怕他有了，也不会出错！

所以我认为就应该这样：class User(Person, Mixin1, Mixin2):

"""


class User(Person, Mixin1, Mixin2):
    def mixin1_method(self):
        print(123)

    def __init__(self, name, age):
        # 使用 super() 调用 Person 的构造函数
        super().__init__(name)  # 这里 super() 将调用 Person 的 __init__ 方法
        # Person.__init__(self, name)
        self.age = age
        print(f"User initialized with age: {self.age}")


# 创建用户对象
user = User("Alice", 30)
print(User.__mro__)

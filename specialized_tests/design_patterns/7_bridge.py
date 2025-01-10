"""
## 桥接模式（Bridge）
> 桥接模式（Bridge）是一种结构型设计模式，旨在将抽象部分和具体实现部分分离，使它们可以独立地变化。

桥接模式的原理实现基于面向对象的多态特性，其核心思想是将抽象部分和实现部分解耦，使得它们可以独立地变化而互不影响。
在桥接模式中，抽象部分和实现部分分别由抽象类和实现类来表示，它们之间通过一个桥梁接口来联系。
```txt
个人见解：
class A 的部分实现由 class C 完成（A draw picture, C fill color）
创建一个 class B，该类不继承 A 但是实现了 A 通过 C 完成的函数

如何重构？
将所有使用 class A 的地方都改成 class B，
好处在于：
```

具体的实现步骤如下：
1. 定义抽象类和实现类：抽象类定义了抽象部分的接口，包含了一些基本的方法。实现类定义了实现部分的接口，包含了一些实现方法。
2. 定义桥梁接口：桥梁接口定义了抽象部分和实现部分之间的连接，它包含了一个对实现类的引用，以及一些委托方法。
3. 定义具体桥梁类：具体桥梁类继承了桥梁接口，实现了委托方法，将调用转发给实现类的方法。
4. 实例化具体桥梁类：在程序运行时，实例化具体桥梁类，并将实现类对象作为参数传递给具体桥梁类的构造函数。
5. 调用具体桥梁类的方法：在程序运行时，调用具体桥梁类的方法，具体桥梁类将委托给实现类的方法来完成具体的操作。

"""
from abc import ABC, abstractmethod


# 抽象类：形状
class Shape(ABC):
    def __init__(self, color):
        self.color = color

    @abstractmethod
    def draw(self):
        pass


# 实现类：颜色
class Color(ABC):
    @abstractmethod
    def fill(self):
        pass


# 桥梁接口
class Bridge(ABC):
    def __init__(self, color: Color):
        self.color = color

    @abstractmethod
    def draw(self):
        pass


# -------------------------------------------------------------------------------------------------------------------- #

# 实现类的具体实现：红色
class RedColor(Color):
    def fill(self):
        return "Red"


# 实现类的具体实现：绿色
class GreenColor(Color):
    def fill(self):
        return "Green"


# 具体桥梁类：圆形
class Circle(Bridge):
    def draw(self):
        return "Circle filled with " + self.color.fill()


# 具体桥梁类：矩形
class Rectangle(Bridge):
    def draw(self):
        return "Rectangle filled with " + self.color.fill()


def main():
    # 使用示例
    red = RedColor()
    green = GreenColor()
    circle = Circle(red)
    rectangle = Rectangle(green)
    print(circle.draw())  # 输出：Circle filled with Red
    print(rectangle.draw())  # 输出：Rectangle filled with Green


if __name__ == '__main__':
    main()

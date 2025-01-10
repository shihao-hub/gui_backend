"""
## 适配器模式（Adapter）
> 适配器模式（Adapter）是一种结构型设计模式，用于将一个类的接口转换为另一个类的接口。
>
> 适配器模式的作用是解决两个不兼容的接口之间的兼容问题，从而使它们能够协同工作。

### 适配器模式由三个主要组件组成：
- 目标接口（Target Interface）：是客户端代码期望的接口。在适配器模式中，它通常由抽象类或接口表示。
- 适配器（Adapter）：是实现目标接口的对象。适配器通过包装一个需要适配的对象，并实现目标接口来实现适配的效果。
- 源接口（Adaptee Interface）：是需要被适配的接口。在适配器模式中，它通常由一个或多个具体类或接口表示。

### 适配器模式通常有两种实现方式：
- 类适配器模式：通过继承来实现适配器，从而使适配器成为源接口的子类，并实现目标接口。这种方式需要适配器能够覆盖源接口的所有方法。
- 对象适配器模式：通过组合来实现适配器，从而使适配器持有一个源接口的对象，并实现目标接口。
  这种方式可以在适配器中自定义需要适配的方法，而无需覆盖源接口的所有方法。

### 优缺点：
适配器模式的优点是能够解决两个不兼容接口之间的兼容问题，并且可以使代码更加灵活和可扩展。

它的缺点是需要额外的适配器对象，可能会导致代码的复杂性增加。在设计过程中，需要根据具体的场景和需求，选择最合适的适配器实现方式。



"""
from abc import ABC


# 目标接口
class Target(ABC):
    def request(self):
        pass


# 源接口
class Adaptee(ABC):
    def specific_request(self):
        pass


# 类适配器：Adapter 继承 Target 是为了实现其定义的函数，继承 Adaptee 是为了代码复用，显然不如对象适配器灵活！
class Adapter(Target, Adaptee):
    def request(self):
        self.specific_request()
        # 其他逻辑


# 对象适配器
class Adapter2(Target):
    def __init__(self, adaptee):
        self._adaptee = adaptee

    def request(self):
        self._adaptee.specific_request()
        # 其他逻辑


# 客户端代码
def client_code(target):
    target.request()


"""
### 个人总结
1. 客户只了解 target 接口。将源对象用一个继承 Target 的类包装后，提供给客户即可。
"""


def main():
    adaptee = Adaptee()
    adapter = Adapter()
    adapter2 = Adapter2(adaptee)

    client_code(adapter)
    client_code(adapter2)


if __name__ == '__main__':
    main()

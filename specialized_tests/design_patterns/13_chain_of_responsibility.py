"""
## 职任链模式（Chain of Responsibility）
> 职责链模式（Chain of Responsibility）是一种行为型设计模式，它通过将请求的发送者和接收者解耦，从而使多个对象都有机会处理这个请求。

### 实现思路
在职责链模式中，我们定义一系列的处理器对象，每个处理器对象都包含一个对下一个处理器对象的引用。
当请求从客户端发送到处理器对象时，第一个处理器对象会尝试处理请求，如果它不能处理请求，
则将请求传递给下一个处理器对象，以此类推，直到请求被处理或者所有的处理器对象都不能处理请求。

### 优缺点
职责链模式的优点是它可以灵活地配置处理器对象的顺序和组合，从而满足不同的处理需求。它还可以将请求的发送者和接收者解耦，从而提高系统的灵活性和可扩展性。
职责链模式的缺点是如果处理器对象过多或者处理器对象之间的关系过于复杂，可能会导致系统的维护难度增加。

### 职责链模式通常涉及的角色
- 处理器接口（Handler Interface）：定义处理器对象的接口，包含处理请求的方法和对下一个处理器对象的引用。
- 具体处理器类（Concrete Handlers）：实现处理器接口，处理请求或将请求传递给下一个处理器对象。
- 客户端（Client）：创建处理器对象的链，将请求发送给链的第一个处理器对象。

### 要点解析
1. foreach 遍历，直到找到能处理请求的处理器对象

"""

"""
    下面是一个简单的 Python 实现示例：
"""


class InterfaceHandler:
    def set_next(self, handler):
        raise NotImplemented

    def handle(self, request):
        raise NotImplemented


class AbstractHandler(InterfaceHandler):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    # Question: 这个命名。。。但是这是为了实现这个设计模式！super() 中的 handle 是传递给下一个处理者，子类的 handle 是判断是否能处理，否则调用 super() 中的 handle。
    def handle(self, request):
        if self._next_handler:
            return self._next_handler.handle(request)
        return None


class ConcreteHandlerA(AbstractHandler):
    def handle(self, request):
        # 是当前具体处理类的处理目标
        if request == "request1":
            return "Handled by ConcreteHandler1"
        else:
            # NOTE: 调用父类的 handle 函数
            return super().handle(request)


class ConcreteHandlerB(AbstractHandler):
    def handle(self, request):
        if request == "request2":
            return "Handled by ConcreteHandler2"
        else:
            return super().handle(request)


class ConcreteHandlerC(AbstractHandler):
    def handle(self, request):
        if request == "request3":
            return "Handled by ConcreteHandler3"
        else:
            return super().handle(request)


"""
### GPT 提供的实际使用场景：客服系统中的请求处理

#### 场景描述
假设我们有一个客户支持系统，响应客户的请求可能涉及多个步骤和不同的支持级别。客户的请求可以是简单的查询，也可以是复杂的问题，需要转接到更高级别的技术支持。我们可以使用职责链模式来设计这个请求处理系统。
1. **请求类型**：
   - 基本查询（如订单状态）
   - 技术问题（如软件故障）
   - 复杂问题（如退款请求）
2. **处理者**：
   - 客服代表（处理基本查询）
   - 技术支持（处理技术问题）
   - 经理（处理复杂问题）

#### 代码示例
以下是一个使用 Python 实现的职责链模式的示例代码：
```python
    class Handler:
        # 处理者的基类
        def __init__(self, successor=None):
            self.successor = successor  # 下一个处理者
        def handle_request(self, request):
            if self.successor:
                self.successor.handle_request(request)
    class CustomerServiceRepresentative(Handler):
        # 客服代表处理基本查询
        def handle_request(self, request):
            if request == "order status":
                print("Customer Service Representative: Here is your order status.")
            else:
                print("Customer Service Representative: I can't handle that request.")
                super().handle_request(request)
    class TechnicalSupport(Handler):
        # 技术支持处理技术问题
        def handle_request(self, request):
            if request == "technical issue":
                print("Technical Support: We'll help you solve your technical issue.")
            else:
                print("Technical Support: I can't handle that request.")
                super().handle_request(request)
    class Manager(Handler):
        # 经理处理复杂问题
        def handle_request(self, request):
            if request == "refund":
                print("Manager: Your refund request has been approved.")
            else:
                print("Manager: I can't handle that request.")
                super().handle_request(request)
    # 创建职责链
    manager = Manager()
    tech_support = TechnicalSupport(successor=manager)
    customer_service = CustomerServiceRepresentative(successor=tech_support)
    # 客户请求处理
    customer_service.handle_request("order status")  # 处理基本查询
    customer_service.handle_request("technical issue")  # 处理技术问题
    customer_service.handle_request("refund")  # 处理复杂问题
    customer_service.handle_request("unknown issue")  # 无法处理的请求
#### 运行结果
```
    Customer Service Representative: Here is your order status.
    Technical Support: We'll help you solve your technical issue.
    Manager: Your refund request has been approved.
    Customer Service Representative: I can't handle that request.
```
"""

"""
    上文的末尾的样例，让我有点体会了：客户端只知道一个入口，发送请求进去，整个通道中有各个责任人，如果请求是当前责任人，则处理，否则继续向后传递
    入口 + 通道 + 传递
"""


def main():
    handler1 = ConcreteHandlerA()
    handler2 = ConcreteHandlerB()
    handler3 = ConcreteHandlerC()

    # 责任链 1 -> 2 -> 3
    handler1.set_next(handler2).set_next(handler3)

    # 发送请求
    requests = ["request1", "request2", "request3", "request4"]
    for request in requests:
        # foreach 1 -> 2 -> 3 -> None
        response = handler1.handle(request)
        if response:
            print(response)
        else:
            print(f"{request} was not handled")


"""
### 代码讲解
- 上面的示例中，我们定义了一个处理器接口 Handler，其中包含 set_next 和 handle 方法。
- 我们还定义了一个抽象处理器类 AbstractHandler，它实现了 set_next 和 handle 方法，其中 handle 方法调用了下一个处理器对象的 handle 方法。
- 我们还实现了三个具体的处理器类 ConcreteHandler1、ConcreteHandler2 和 ConcreteHandler3，它们分别实现了自己的 handle 方法。
- 客户端创建处理器对象的链，将处理器对象按照需要连接起来，然后将请求发送给链的第一个处理器对象，处理器对象将请求进行处理或者将请求传递给下一个处理器对象，直到请求被处理或者没有处理器对象能够处理请求。
- 在这个例子中，当请求为 "request1"、"request2"、"request3" 时，请求会被相应的处理器对象处理；当请求为 "request4" 时，没有处理器对象能够处理该请求，因此该请求未被处理。
总的来说，职责链模式可以使多个对象都有机会处理请求，并且可以灵活地配置处理器对象的顺序和组合，从而提高系统的灵活性和可扩展性。
"""

if __name__ == '__main__':
    main()

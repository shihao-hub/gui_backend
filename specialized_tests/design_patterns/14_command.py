"""
## 命令模式（Command）
> 命令模式（Command）是一种行为型设计模式，它将请求封装成一个对象，从而使您可以将不同的请求与其请求的接收者分开。  <br>
> 这种模式的目的是通过将请求发送者和请求接收者解耦来实现请求的发送、执行和撤销等操作。  <br>

### 实现思路
- 在命令模式中，我们定义一个 Command 接口，该接口包含一个 execute 方法，用于执行命令。
- 我们还定义了一个 Invoker 类，它用于发送命令，可以接受一个 Command 对象，并在需要时调用该对象的 execute 方法。
- 我们还定义了一个 Receiver 类，它实际执行命令，包含一些特定于应用程序的业务逻辑。

### 命令模式涉及以下角色
- Command 接口：定义了一个执行命令的方法 execute。
- 具体命令类（Concrete Command）：实现了 Command 接口，实现 execute 方法，包含一个接收者对象，执行具体的业务逻辑。
- Invoker 类：负责发送命令，它包含一个 Command 对象，可以在需要时调用该对象的 execute 方法。
- Receiver 类：包含一些特定于应用程序的业务逻辑，实际执行命令。

### 个人使用理解
- Command 是命令对象，Invoker 是调用管理者，Receiver 是接收命令者
> 命令模式并不是为实现命令执行逻辑提供的，但是假如我实现执行各种命令，显然可以这样实现  <br>
> Receiver 和 Command 绑定，Invoker 管理命令，根据用户的命令字符串创建对应的命令来调用  <br>

"""
from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass


class Invoker(ABC):
    pass


class Receiver(ABC):
    pass


# -------------------------------------------------------------------------------------------------------------------- #
class RemoteControl(Invoker):
    def __init__(self):
        self.commands: List[Command] = []

    def add_command(self, command: Command):
        self.commands.append(command)

    def remove_command(self, command: Command):
        pass

    def execute_commands(self):
        for command in self.commands:
            command.execute()


# -------------------------------------------------------------------------------------------------------------------- #

class Light(Receiver):

    def create_light_on_command(self):
        return LightOnCommand(self)

    def create_light_off_command(self):
        return LightOffCommand(self)

    def turn_on(self):
        print("The light is on")

    def turn_off(self):
        print("The light is off")


class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self):
        self.light.turn_on()


class LightOffCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self):
        self.light.turn_off()


# -------------------------------------------------------------------------------------------------------------------- #


def main():
    # 可以被控制的目标
    light = Light()

    # 类比遥控器
    remote_control = RemoteControl()

    # 类比遥控器按键
    remote_control.add_command(light.create_light_on_command())  # <==> Light.create_light_on_command(light)
    remote_control.add_command(light.create_light_off_command())

    # 执行命令
    remote_control.execute_commands()


"""
### 代码解释
- 在这个例子中，我们首先定义了一个 Command 接口，该接口包含 execute 方法。然后，我们定义了两个具体命令类 LightOnCommand 和 LightOffCommand，
  它们实现了 Command 接口，并包含一个接收者对象 Light，实现了执行具体的业务逻辑。
- 我们还定义了一个 Invoker 类 RemoteControl，它包含一个 Command 对象的列表，并提供了一个 add_command 方法用于添加 Command 对象。
  execute_commands 方法用于在需要时调用 Command 对象的 execute 方法。
- 最后，我们定义了一个 Receiver 类 Light，它包含一些特定于应用程序的业务逻辑，实际执行命令。
- 在客户端代码中，我们创建了一个 Light 对象和一个 RemoteControl 对象。
  我们将 LightOnCommand 和 LightOffCommand 对象添加到 RemoteControl 对象的命令列表中，然后调用 execute_commands 方法来执行这些命令。
"""

if __name__ == '__main__':
    main()

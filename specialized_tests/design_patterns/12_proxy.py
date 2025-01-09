"""
## 代理模式
> 代理模式（Proxy）是一种结构型设计模式，它允许在访问对象时添加一些额外的行为。代理类充当客户端和实际对象之间的中介。
> 客户端通过代理来访问实际对象，代理在访问实际对象前后执行一些额外的操作，例如权限检查、缓存等。

代理模式包含三个角色：抽象主题（Subject）、真实主题（Real Subject）和代理主题（Proxy Subject）。
其中，抽象主题定义了真实主题和代理主题的公共接口；真实主题是实际执行操作的对象；代理主题通过实现抽象主题接口，控制对真实主题的访问。

### 要点解析
1. 对于“客户端通过代理来访问实际对象，代理在访问实际对象前后执行一些额外的操作，例如权限检查、缓存等”，这挺像 Decorator 的呀？

"""

# 关于代理模式，Python 还是 Java 好像有个 Proxy 之前见过

""" 
    下面是一个 Python 实现的示例，假设我们有一个邮件服务器，我们需要实现一个邮件客户端程序，但我们不想直接连接到邮件服务器，
    因为这样可能会存在一些风险，我们想通过代理来连接邮件服务器，以此增加一些安全性：
    
    但是，下面的内容没有体现出如何解决风险的...
"""


class AbstractEmail:
    # 抽象主题
    def send(self, message):
        raise NotImplemented


class EmailServer(AbstractEmail):
    # 真实主题
    def send(self, message):
        print(f'Sending email: {message}')


class EmailProxy(AbstractEmail):
    # 代理主题
    def __init__(self, email_server):
        self.email_server = email_server

    def send(self, message):
        if self.is_allowed_to_send(message):
            self.email_server.send(message)
            self.log(message)
        else:
            print('Not allowed to send email')

    def is_allowed_to_send(self, message):
        # Check if user is allowed to send the email
        return True

    def log(self, message):
        # Log the email to a file
        print(f'Logging email: {message}')


if __name__ == '__main__':
    email_proxy = EmailProxy(EmailServer())
    email_proxy.send('Hello, world!')

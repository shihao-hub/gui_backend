from abc import ABC, abstractmethod

from xmlrpc import server


class ServerInterface(ABC):
    # 定义 ServerInterface 的目的是，子类的函数中未使用 self，pycharm 不会有警告
    @abstractmethod
    def add(self, x, y):
        pass


class Server(ServerInterface):
    def add(self, x, y):
        return x + y


def main():
    with server.SimpleXMLRPCServer(("localhost", 8081)) as server_obj:
        server_obj.register_instance(Server())
        print("Server is running...")
        server_obj.serve_forever()


if __name__ == '__main__':
    main()

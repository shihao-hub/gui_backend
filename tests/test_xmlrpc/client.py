from xmlrpc import client


def main():
    proxy = client.ServerProxy("http://localhost:8081/")
    print(proxy.add(4, 5))  # 输出 9


if __name__ == '__main__':
    main()

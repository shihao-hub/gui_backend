# TODO: 模拟实现一个事件循环主线程
def event_loop():
    class Local:
        pass

    loc = Local()

    while True:
        # 主线程循环执行，监听事件的到来
        # 联想之前用 lua 实现的功能，应该要涉及底层的 select 或 epoll 吧？
        pass


if __name__ == '__main__':
    event_loop()

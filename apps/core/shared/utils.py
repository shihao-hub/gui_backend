import functools


def knowledge(*_):
    # TODO: 目前只是充当注释，后续此处可以统计一个知识库。
    #   **func_name - func_no - func_location**
    #   - knowledge1
    #   - knowledge2
    #   - knowledge3
    def outer(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return outer

def divide(a, b):
    return a / b
def main():
    try:
        # 假设这里我们试图除以零
        result = divide(10, 0)
    except ZeroDivisionError as e:
        print(f"捕获到异常: {e}")
        # 在处理上面的异常时，我们尝试访问一个未定义的变量
        print(undefined_variable)
if __name__ == "__main__":
    main()

# NOTE:
#   并发是伪并行
#   并行是真正的并行
import functools
from concurrent.futures import ThreadPoolExecutor, as_completed


@functools.cache
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def main():
    numbers = map(lambda x: x * 2, [100, 21, 22, 23, 24, 25])
    # NOTE:
    #   此处很像所谓的协同和同步，as_completed 就是同步，futures 就是 协同 或者 伪并行 或者 并行
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fibonacci, e) for e in numbers]
        print(max(e.result() for e in as_completed(futures)))


if __name__ == '__main__':
    main()

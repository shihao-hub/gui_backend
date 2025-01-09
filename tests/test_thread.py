import threading

N = 1000
sum_value = 0


def thread_sum():
    global sum_value
    for i in range(N):
        sum_value += 1


def main():
    thread_a = threading.Thread(target=thread_sum)
    thread_b = threading.Thread(target=thread_sum)
    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()
    print(f" cur: {sum_value}")
    print(f"real: {N * 2}")


if __name__ == '__main__':
    main()

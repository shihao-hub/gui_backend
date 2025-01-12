def fn():
    def fn2():
        print(x)

    x = 1
    fn2()


fn()
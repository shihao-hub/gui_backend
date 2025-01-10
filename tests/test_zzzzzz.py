import inspect
import sys
import traceback


def test_01():
    class Local:
        pass

    loc = Local()


def test_02():
    class Local:
        pass

    loc = Local()


try:
    print(t.a)
except Exception as e:
    # frame = inspect.stack()[0]
    # print(str(frame.filename) + ":" + str(frame.lineno) + ": " + str(e))
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb)
    last_trace = tb[-1]
    print(str(last_trace.filename) + ":" + str(last_trace.lineno) + ": " + str(e))

if __name__ == '__main__':
    test_01()
    test_02()

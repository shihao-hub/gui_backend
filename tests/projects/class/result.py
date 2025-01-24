__all__ = ["Result"]

import random
from typing import TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class ResultPrivateFields:
    def __init__(self):
        self.value = None
        self.error = None


class Result[T, U]:
    def __init__(self, value: Union[T, None] = None, error: Union[U, None] = None):
        self._ = ResultPrivateFields()

        self._.value = value
        self._.error = error

    @classmethod
    def ok(cls, value: T) -> "Result[T, U]":
        return cls(value=value)

    @classmethod
    def err(cls, error: U) -> "Result[T, U]":
        return cls(error=error)

    def is_ok(self) -> bool:
        return self._.error is None

    def is_err(self) -> bool:
        return self._.error is not None

    def get_value(self) -> T:
        if self.is_ok():
            return self._.value
        raise ValueError("Attempted to get value from an Err Result")

    def get_error(self) -> U:
        if self.is_err():
            return self._.error
        raise ValueError("Attempted to get error from an Ok Result")


if __name__ == '__main__':
    def fn1() -> Result[int, str]:
        if random.random() < 0.5:
            return Result.err("error")
        return Result.ok(1)


    res = fn1()
    if res.is_ok():
        print(res.get_value())
    else:
        print(res.get_error())


    def info(format_str, *args):
        pass

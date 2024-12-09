import logging
from typing import Tuple


class Log:
    def __init__(self, logger_name="print"):
        # 调试、信息、警告、错误、严重、致命
        self._logger = logging.getLogger(logger_name)

    def _convert(self, arg: Tuple):
        this = self
        return f"{"\t".join(map(str, arg))}"

    def debug(self, *arg):
        self._logger.debug("%s", self._convert(arg))

    def info(self, *arg):
        self._logger.info("%s", self._convert(arg))

    def warning(self, *arg):
        self._logger.warning("%s", self._convert(arg))

    def error(self, *arg):
        self._logger.error("%s", self._convert(arg))

    def critical(self, *arg):
        self._logger.fatal("%s", self._convert(arg))

    def fatal(self, *arg):
        self._logger.fatal("%s", self._convert(arg))


if __name__ == '__main__':
    pass

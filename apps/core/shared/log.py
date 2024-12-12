import logging
import traceback
from typing import Tuple


class Log:
    def __init__(self, logger_name="print"):
        # 调试、信息、警告、错误、严重、致命
        self._logger = logging.getLogger(logger_name)

    def debug(self, s: str):
        self._logger.debug("%s", s)

    def info(self, s: str):
        self._logger.info("%s", s)

    def warning(self, s: str):
        self._logger.warning("%s", s)

    def error(self, s: str, print_stack=False):
        if print_stack:
            s += f"\n{traceback.format_exc()}"
        self._logger.error("%s", s)

    def critical(self, s: str):
        self._logger.fatal("%s", s)

    def fatal(self, s: str):
        self._logger.fatal("%s", s)


if __name__ == '__main__':
    pass

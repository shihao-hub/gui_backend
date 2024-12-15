import logging
import traceback
from typing import Tuple, Union, Any


class Log:
    def __init__(self, logger_name="print"):
        # 调试、信息、警告、错误、严重、致命
        self._logger = logging.getLogger(logger_name)

    def debug(self, s: Any):
        self._logger.debug("%s", f"{s}")

    def info(self, s: Any):
        self._logger.info("%s", f"{s}")

    def warning(self, s: Any):
        self._logger.warning("%s", f"{s}")

    def error(self, s: Any, print_stack=False):
        if print_stack:
            s += f"\n{traceback.format_exc()}"
        self._logger.error("%s", f"{s}")

    def critical(self, s: Any):
        self._logger.fatal("%s", f"{s}")

    def fatal(self, s: Any):
        self._logger.fatal("%s", s)


if __name__ == '__main__':
    pass

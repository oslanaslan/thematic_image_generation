import logging
from sys import exc_info

import loguru
# import logging_loki


# logging_loki.emitter.LokiEmitter.level_tag = "level"
LOG_PATH = "../../volumes/log/log.log"


class GrafanaLogger:

    def __init__(self) -> None:
        self.console_logger = loguru.logger
        self.console_logger.add(LOG_PATH)
        # handler = logging_loki.LokiHandler(
        #     url="http://loki:3100/loki/api/v1/push",
        #     version="1",
        # )
        # self.loki_logger = logging.getLogger("app-logger")
        # self.loki_logger.setLevel(logging.DEBUG)
        # self.loki_logger.addHandler(handler)


    def error(self, msg: str, exc_info: Exception) -> None:
        self.console_logger.exception(msg, exc_info=exc_info)
        # self.loki_logger.error(msg)


    def info(self, msg: str) -> None:
        self.console_logger.info(msg)
        # self.loki_logger.info(msg)


    def debug(self, msg: str) -> None:
        self.console_logger.debug(msg)
        # self.loki_logger.debug(msg)


if __name__ == "__main__":
    raise NotImplementedError()

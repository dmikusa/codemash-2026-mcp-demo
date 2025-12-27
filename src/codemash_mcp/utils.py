import json
import logging
import os
import time

from fastmcp import FastMCP


class McpRunner:
    def __init__(self, mcp: FastMCP):
        self._mcp = mcp

    def test(self):
        return self._mcp

    def run(self):
        self._mcp.run(transport="streamable-http")

    def host(self):
        return self._mcp.http_app(transport="streamable-http")


class JsonFormatter(logging.Formatter):
    converter = time.gmtime

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "name": record.name,
            "mcp": record.__dict__.get("mcp", {}),
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


# This is all to force FastMCP to log as JSON
#
# See https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/utilities/logging.py#L22
# for what FastMCP does to set up its logging. If that changes, then we might need to
# adapt this strategy for overriding it.
#
def _force_json_logging():
    default_log_level = os.environ.get("LOG_LEVEL", "DEBUG")

    """Force all loggers to use JSON formatting"""
    root_logger = logging.getLogger()

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(default_log_level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(console_handler)

    # Reconfigure all existing loggers
    for logger in logging.getLogger().manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            logger.propagate = True
            logger.setLevel(default_log_level)

    # Override the logger class to ensure new loggers use JSON formatting
    class JsonLogger(logging.getLoggerClass()):
        def __init__(self, name, level=default_log_level):
            super().__init__(name, level)
            self.propagate = True

        def __setattr__(self, name, value) -> None:
            if name == "propagate":
                value = True
            super().__setattr__(name, value)

        def removeHandler(self, hdlr) -> None:
            pass

        def addHandler(self, hdlr) -> None:
            pass

        def removeFilter(self, filter) -> None:
            pass

        def addFilter(self, filter) -> None:
            pass

    logging.setLoggerClass(JsonLogger)

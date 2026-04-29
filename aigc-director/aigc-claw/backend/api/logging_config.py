import logging
import os
import queue
import sys
from logging.handlers import QueueHandler, QueueListener

_listener = None


class AIGCFormatter(logging.Formatter):
    """Compact, Pixelle-like console formatter for API and worker logs."""

    LEVEL_ICONS = {
        "DEBUG": ".",
        "INFO": "i",
        "WARNING": "!",
        "ERROR": "x",
        "CRITICAL": "X",
    }

    def format(self, record: logging.LogRecord) -> str:
        record.level_icon = self.LEVEL_ICONS.get(record.levelname, record.levelname[:1])
        return super().format(record)


def setup_concurrent_logging():
    """Configure queue-based logging so worker threads do not interleave output."""
    global _listener
    if _listener is not None:
        return _listener

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    log_queue = queue.Queue(-1)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(AIGCFormatter(
        "%(asctime)s | %(level_icon)s %(levelname)-7s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%H:%M:%S",
    ))

    listener = QueueListener(log_queue, console_handler, respect_handler_level=True)
    listener.start()

    queue_handler = QueueHandler(log_queue)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(queue_handler)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "httpx"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(logging.WARNING if name == "httpx" else level)

    _listener = listener
    return listener

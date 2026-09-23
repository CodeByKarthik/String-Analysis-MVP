from __future__ import annotations

import logging
import sys

import structlog

LOG_FORMAT = "%(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    configure_logging()
    return structlog.get_logger(name)

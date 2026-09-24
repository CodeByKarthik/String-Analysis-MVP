from __future__ import annotations

import logging
import sys

import structlog

LOG_FORMAT = "%(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class MetricsAccessFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not (
            record.name == "uvicorn.access"
            and len(record.args) >= 3  # type: ignore[arg-type]
            and str(record.args[2]).split("?", maxsplit=1)[0]  # type: ignore[index]
            == "/metrics"
        )


def configure_logging(level: str = "INFO") -> None:
    """
    Configure the logging settings for the application.

    Args:
        level (str, optional): The logging level. Defaults to "INFO".
    """
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
    logging.getLogger("uvicorn.access").addFilter(MetricsAccessFilter())


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name (str): The name of the logger.

    Returns:
        structlog.BoundLogger: The configured logger instance.
    """
    configure_logging()
    return structlog.get_logger(name)

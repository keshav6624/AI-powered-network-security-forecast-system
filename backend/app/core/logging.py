"""
NetGuard AI — Structured Logging
"""
import logging
import sys
from typing import Any

try:
    import structlog  # type: ignore
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False

from app.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if HAS_STRUCTLOG:
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer() if settings.app_env == "production"
                else structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
            cache_logger_on_first_use=True,
        )
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            stream=sys.stdout,
        )


def get_logger(name: str) -> Any:
    if HAS_STRUCTLOG:
        import structlog as sl
        return sl.get_logger(name)
    return logging.getLogger(name)

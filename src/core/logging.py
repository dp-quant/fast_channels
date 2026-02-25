"""Custom logger for the application."""

import orjson
import traceback
from loguru import logger
from src.core.config import settings, Settings


__all__ = ["logger"]


def serialize(record):
    """Serialize a log record. Simplified version of the original serialize function."""
    subset = {
        "time": record["time"].isoformat(),
        "message": record["message"],
        "level": record["level"].name,
    }
    if "extra" in record:
        subset.update(record["extra"])

    if exc_info := subset.get("exc_info"):
        subset["exception"] = {
            "type": exc_info.__class__.__name__,
            "message": str(exc_info),
            "traceback": traceback.format_exception(exc_info),
        }
        subset.pop("exc_info", None)
    return orjson.dumps(subset).decode("utf-8")


def sink(message):
    """Custom sink for Loguru."""
    serialized = serialize(message.record)
    print(serialized)


def configure_logger(settings: Settings) -> None:
    """Configure the logger."""
    logger.remove()
    logger.add(sink, level=settings.log_level.upper())


configure_logger(settings)

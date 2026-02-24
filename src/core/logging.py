"""Custom logger for the application."""

import orjson
from loguru import logger
from src.core.config import settings, Settings


__all__ = ["logger"]


def serialize(record):
    """Serialize a log record."""
    subset = {
        "time": record["time"].isoformat(),
        "message": record["message"],
        "level": record["level"].name,
    }
    if "extra" in record:
        subset.update(record["extra"])
    if record.get("exception"):
        subset["exception"] = {
            "type": record.get("exception").__class__.__name__,
            "message": str(record.get("exception")),
            "traceback": record.get("exception").traceback,
        }
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
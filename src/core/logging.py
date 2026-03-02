"""Custom logger for the application."""

import orjson
import sys
from loguru import logger
from opentelemetry import trace
from src.core.config import settings, Settings


__all__ = ["logger"]


def otel_patcher(record):
    """
    Injects OpenTelemetry trace/span IDs and resource attributes
    into the record's extra dictionary.
    """
    span_context = trace.get_current_span().get_span_context()
    
    if span_context.is_valid:
        record["extra"]["trace_id"] = format(span_context.trace_id, "032x")
        record["extra"]["span_id"] = format(span_context.span_id, "016x")

    record["extra"]["severity_text"] = record["level"].name
    record["extra"]["service.name"] = settings.service_name
    record["extra"]["service.version"] = settings.version

    return record

def serialize(message):
    """
    Custom serializer to map Loguru's internal structure 
    to OTel-compliant JSON keys.
    """
    record = message.record
    subset = {
        "timestamp": record["time"].isoformat(),
        "severity_text": record["extra"].get("severity_text"),
        "body": record["message"],
        "trace_id": record["extra"].get("trace_id"),
        "span_id": record["extra"].get("span_id"),
        "resource": {
            "service.name": record["extra"].get("service.name"),
            "service.version": record["extra"].get("service.version"),
        },
        "attributes": record["extra"]  # Catch-all for other 'extra' data
    }
    exception = record.get("exception")
    if exception:
        subset["exception.type"] = exception.type.__name__
        subset["exception.message"] = str(exception.value)
        subset["exception.stacktrace"] = record["exception"].traceback
    return orjson.dumps(subset).decode("utf-8")


def sink(message):
    """Custom sink for Loguru."""
    serialized = serialize(message)
    print(serialized, file=sys.stdout)


def configure_logger(settings: Settings):
    """Configure and return a patched logger."""
    base_logger = logger
    base_logger.remove()
    
    patched_logger = base_logger.patch(otel_patcher)
    patched_logger.add(sink, level=settings.log_level.upper())
    return patched_logger


logger = configure_logger(settings)

"""
Transformations between internal and proto models.

Prefer to keep explicit types conversions for clarity and maintainability.
"""

from .base import datetime_to_timestamp, timestamp_to_datetime

__all__ = ["timestamp_to_datetime", "datetime_to_timestamp"]

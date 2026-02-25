from datetime import datetime, timezone
from google.protobuf import timestamp_pb2


def timestamp_to_datetime(ts) -> datetime:
    """Convert proto Timestamp to timezone-aware datetime."""
    if ts is None:
        return datetime.now(timezone.utc)
    return ts.ToDatetime().replace(tzinfo=timezone.utc)


def datetime_to_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
    """Convert timezone-aware datetime to proto Timestamp."""
    return timestamp_pb2.Timestamp(
        seconds=int(dt.timestamp()),
        nanos=int(dt.microsecond * 1000),
    )

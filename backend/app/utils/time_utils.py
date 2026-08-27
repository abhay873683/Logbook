from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def calculate_duration_seconds(
    start_time: datetime,
    end_time: datetime,
) -> int:
    if end_time <= start_time:
        raise ValueError("End time must be after start time")

    return int((end_time - start_time).total_seconds())
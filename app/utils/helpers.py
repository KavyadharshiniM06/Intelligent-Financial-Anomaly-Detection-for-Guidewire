from datetime import datetime, timezone


# Generic helper functions can be added here
def format_response(data: dict) -> dict:
    return {"data": data, "success": True}


def to_naive_utc(value: datetime) -> datetime:
    """
    Normalize datetimes for models backed by TIMESTAMP WITHOUT TIME ZONE.
    """
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)

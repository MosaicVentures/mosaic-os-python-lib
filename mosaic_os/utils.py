from datetime import datetime, timezone
from typing import Any


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


def combine_person_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}"


def json_serializer(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not supported")

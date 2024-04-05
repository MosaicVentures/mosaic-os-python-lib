from datetime import datetime, timezone


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


def combine_person_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}"

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .errors import ApiError


def parse_uuid(value: str, *, field: str = "id") -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except Exception as exc:
        raise ApiError(400, "bad_request", f"Invalid UUID for '{field}'.") from exc


def iso_timestamp(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

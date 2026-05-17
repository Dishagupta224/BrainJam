from __future__ import annotations

from typing import Any

from flask import Request

from .errors import ApiError


def require_json(request: Request) -> dict[str, Any]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError(400, "bad_request", "Request body must be JSON object.")
    return data


def get_str(data: dict[str, Any], key: str, *, required: bool = True, max_len: int | None = None) -> str | None:
    value = data.get(key)
    if value is None:
        if required:
            raise ApiError(400, "bad_request", f"Missing field: {key}.")
        return None
    if not isinstance(value, str):
        raise ApiError(400, "bad_request", f"Field '{key}' must be a string.")
    value = value.strip()
    if required and not value:
        raise ApiError(400, "bad_request", f"Field '{key}' must not be empty.")
    if max_len is not None and len(value) > max_len:
        raise ApiError(400, "bad_request", f"Field '{key}' is too long.")
    return value


def get_int(data: dict[str, Any], key: str, *, required: bool = True, min_value: int | None = None, max_value: int | None = None) -> int | None:
    value = data.get(key)
    if value is None:
        if required:
            raise ApiError(400, "bad_request", f"Missing field: {key}.")
        return None
    if not isinstance(value, int):
        raise ApiError(400, "bad_request", f"Field '{key}' must be an integer.")
    if min_value is not None and value < min_value:
        raise ApiError(400, "bad_request", f"Field '{key}' must be >= {min_value}.")
    if max_value is not None and value > max_value:
        raise ApiError(400, "bad_request", f"Field '{key}' must be <= {max_value}.")
    return value


def get_bool(data: dict[str, Any], key: str, *, required: bool = True) -> bool | None:
    value = data.get(key)
    if value is None:
        if required:
            raise ApiError(400, "bad_request", f"Missing field: {key}.")
        return None
    if not isinstance(value, bool):
        raise ApiError(400, "bad_request", f"Field '{key}' must be a boolean.")
    return value

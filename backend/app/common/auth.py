from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

import jwt
from flask import current_app, g, request

from .errors import ApiError

F = TypeVar("F", bound=Callable[..., Any])


def _get_bearer_token() -> str:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise ApiError(401, "unauthorized", "Missing or invalid Authorization header.")
    token = header.removeprefix("Bearer ").strip()
    if not token:
        raise ApiError(401, "unauthorized", "Missing bearer token.")
    return token


def decode_token(token: str) -> dict[str, Any]:
    secret = current_app.config.get("SECRET_KEY")
    if not secret:
        raise ApiError(500, "internal_error", "Server misconfigured (missing SECRET_KEY).")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise ApiError(401, "unauthorized", "Token expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise ApiError(401, "unauthorized", "Invalid token.") from exc
    if not isinstance(payload, dict):
        raise ApiError(401, "unauthorized", "Invalid token payload.")
    return payload


def auth_required(fn: F) -> F:
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        token = _get_bearer_token()
        payload = decode_token(token)
        sub = payload.get("sub")
        try:
            user_id = int(sub)
        except Exception as exc:
            raise ApiError(401, "unauthorized", "Invalid token subject.") from exc
        g.user_id = user_id
        g.token_payload = payload
        return fn(*args, **kwargs)

    return cast(F, wrapper)

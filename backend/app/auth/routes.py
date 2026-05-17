import re
from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, current_app, jsonify, request, g
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.common.auth import auth_required
from app.common.errors import ApiError
from app.common.validators import require_json, get_str
from app.extensions import db
from app.models import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

_USERNAME_RE = re.compile(r"^[a-z0-9_]{3,64}$")


@bp.post("/register")
def register():
    # Phase 5: create user + return JWT and user summary
    data = require_json(request)
    username_raw = get_str(data, "username", max_len=64)
    email_raw = get_str(data, "email", max_len=255)
    password = get_str(data, "password", max_len=255)

    username = _normalize_username(username_raw)
    email = _normalize_email(email_raw)
    _validate_password(password)

    password_hash = generate_password_hash(password)
    display_name = username_raw.strip()

    user = User(email=email, username=username, password_hash=password_hash, display_name=display_name)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ApiError(409, "conflict", "Email or username already exists.") from exc

    token = _issue_token(user)
    return jsonify({"token": token, "user": _user_summary(user)}), 200


@bp.post("/login")
def login():
    # Phase 5: verify credentials + return JWT and user summary
    data = require_json(request)
    identifier_raw = get_str(data, "identifier", max_len=255)
    password = get_str(data, "password", max_len=255)

    identifier = identifier_raw.strip()
    user = None
    if "@" in identifier:
        user = User.query.filter_by(email=_normalize_email(identifier)).one_or_none()
    if user is None:
        user = User.query.filter_by(username=_normalize_username(identifier)).one_or_none()

    if user is None or not check_password_hash(user.password_hash, password):
        raise ApiError(401, "unauthorized", "Invalid credentials.")

    token = _issue_token(user)
    return jsonify({"token": token, "user": _user_summary(user)}), 200

@bp.get("/me")
@auth_required
def auth_me():
    user = db.session.get(User, int(g.user_id))
    if not user:
        raise ApiError(401, "unauthorized", "Invalid token.")
    return jsonify(_user_summary(user)), 200


def _issue_token(user: User) -> str:
    secret = current_app.config.get("SECRET_KEY")
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=7)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_username(username: str) -> str:
    username = username.strip().lower()
    if not _USERNAME_RE.match(username):
        raise ApiError(400, "bad_request", "Username must be 3-64 chars of a-z, 0-9, or underscore.")
    return username


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise ApiError(400, "bad_request", "Password must be at least 8 characters.")


def _user_summary(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "displayName": user.display_name or user.username,
    }

from flask import Blueprint, jsonify, g

from app.common.auth import auth_required
from app.common.errors import ApiError
from app.extensions import db
from app.models import User

bp = Blueprint("users", __name__, url_prefix="/api")


@bp.get("/me")
@auth_required
def me():
    # Compatibility route: same as /api/auth/me
    user = db.session.get(User, int(g.user_id))
    if not user:
        raise ApiError(401, "unauthorized", "Invalid token.")
    return jsonify({"id": user.id, "username": user.username, "displayName": user.display_name or user.username}), 200

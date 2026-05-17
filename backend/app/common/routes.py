from flask import Blueprint

bp = Blueprint("common", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    return "OK", 200

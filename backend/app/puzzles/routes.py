from flask import Blueprint, jsonify, request
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.common.errors import ApiError
from app.models import PuzzlePack, PuzzleTask

bp = Blueprint("puzzles", __name__, url_prefix="/api")

def _norm(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _pack_summary(pack: PuzzlePack) -> dict:
    task_count = len(pack.tasks) if pack.tasks is not None else 0
    return {
        "id": pack.slug,
        "title": pack.title,
        "genre": pack.genre,
        "difficulty": pack.difficulty,
        "description": pack.description,
        "estimatedMinutes": pack.estimated_minutes,
        "taskCount": task_count,
    }


def _task_payload(task: PuzzleTask) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "prompt": task.prompt,
        "orderIndex": task.order_index,
        "difficulty": task.difficulty,
    }


@bp.get("/puzzles/genres")
def list_genres():
    try:
        rows = (
            db.session.query(PuzzlePack.genre)
            .filter(PuzzlePack.is_active.is_(True))
            .distinct()
            .order_by(PuzzlePack.genre)
            .all()
        )
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    return jsonify([r[0] for r in rows if r and r[0]]), 200


@bp.get("/puzzles")
def list_puzzles():
    genre = _norm(request.args.get("genre"))
    difficulty = _norm(request.args.get("difficulty"))

    try:
        query = (
            PuzzlePack.query.filter(PuzzlePack.is_active.is_(True))
            .options(joinedload(PuzzlePack.tasks))
            .order_by(PuzzlePack.title.asc())
        )

        if genre:
            query = query.filter(db.func.lower(PuzzlePack.genre) == genre.lower())
        if difficulty:
            query = query.filter(db.func.lower(PuzzlePack.difficulty) == difficulty.lower())

        packs = query.all()
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    return jsonify([_pack_summary(pack) for pack in packs]), 200


@bp.get("/puzzles/<puzzle_id>")
def get_puzzle(puzzle_id: str):
    try:
        pack = (
            PuzzlePack.query.filter_by(slug=puzzle_id, is_active=True)
            .options(joinedload(PuzzlePack.tasks))
            .one_or_none()
        )
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    if not pack:
        return jsonify({"error": "not_found", "message": "Puzzle not found."}), 404

    tasks_sorted = sorted(pack.tasks or [], key=lambda t: (t.order_index or 0, t.id or 0))
    return jsonify(
        {
            **_pack_summary(pack),
            "tasks": [_task_payload(task) for task in tasks_sorted],
        }
    ), 200

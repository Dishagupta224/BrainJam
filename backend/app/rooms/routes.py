from __future__ import annotations

import random
import string

from flask import Blueprint, jsonify, request, g
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy.orm import joinedload

from app.common.auth import auth_required
from app.common.errors import ApiError
from app.common.validators import get_bool, get_int, get_str, require_json
from app.extensions import db
from app.models import PuzzlePack, Room, RoomMember, RoomRole, RoomStatus, User

bp = Blueprint("rooms", __name__, url_prefix="/api")


def _invite_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def _room_payload(room: Room) -> dict:
    members = [
        {
            "id": member.user.id,
            "username": member.user.username,
            "role": member.role.value if hasattr(member.role, "value") else str(member.role),
            "ready": bool(member.ready),
        }
        for member in (room.members or [])
        if member.left_at is None
    ]

    all_ready = all(m["ready"] for m in members if m["role"] != RoomRole.SPECTATOR.value)
    return {
        "id": str(room.id),
        "ownerId": room.owner_id,
        "inviteCode": room.invite_code,
        "status": room.status.value if hasattr(room.status, "value") else str(room.status),
        "locked": bool(room.locked),
        "maxPlayers": int(room.max_players),
        "ownerParticipates": bool(room.owner_participates),
        "allMembersReady": all_ready,
        "puzzle": {
            "id": room.puzzle_pack.slug,
            "title": room.puzzle_pack.title,
            "genre": room.puzzle_pack.genre,
            "difficulty": room.puzzle_pack.difficulty,
        },
        "members": members,
    }


def _active_participant_count(room: Room) -> int:
    return sum(1 for m in (room.members or []) if m.left_at is None and m.role != RoomRole.SPECTATOR)


@bp.post("/rooms")
@auth_required
def create_room():
    data = require_json(request)

    puzzle_id = get_str(data, "puzzleId", max_len=200)
    max_players = get_int(data, "maxPlayers", required=False, min_value=2, max_value=4) or 4
    owner_participates = get_bool(data, "ownerParticipates", required=False)
    owner_participates = True if owner_participates is None else owner_participates

    try:
        puzzle = PuzzlePack.query.filter_by(slug=puzzle_id, is_active=True).one_or_none()
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    if not puzzle:
        raise ApiError(404, "not_found", "Puzzle not found.")

    try:
        owner = db.session.get(User, int(g.user_id))
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    if not owner:
        raise ApiError(401, "unauthorized", "Invalid token.")

    # Generate a unique invite code (retry on collisions).
    invite_code = None
    for _ in range(10):
        candidate = _invite_code()
        try:
            exists = db.session.query(Room.id).filter_by(invite_code=candidate).first()
        except (OperationalError, ProgrammingError) as exc:
            db.session.rollback()
            raise ApiError(503, "service_unavailable", "Database not ready.") from exc
        if not exists:
            invite_code = candidate
            break
    if invite_code is None:
        raise ApiError(500, "internal_error", "Could not generate invite code.")

    room = Room(
        owner_id=owner.id,
        puzzle_pack_id=puzzle.id,
        invite_code=invite_code,
        status=RoomStatus.LOBBY,
        max_players=max_players,
        locked=False,
        owner_participates=owner_participates,
    )
    db.session.add(room)
    db.session.flush()

    owner_role = RoomRole.OWNER if owner_participates else RoomRole.SPECTATOR
    db.session.add(
        RoomMember(
            room_id=room.id,
            user_id=owner.id,
            role=owner_role,
            ready=False,
        )
    )

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ApiError(409, "conflict", "Unable to create room (conflict).") from exc

    try:
        room = (
            Room.query.options(joinedload(Room.members).joinedload(RoomMember.user), joinedload(Room.puzzle_pack))
            .filter_by(id=room.id)
            .one()
        )
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    return jsonify(_room_payload(room)), 200


@bp.post("/rooms/join")
@auth_required
def join_room():
    data = require_json(request)
    invite_code = (get_str(data, "inviteCode", max_len=16) or "").strip().upper()
    if not invite_code:
        raise ApiError(400, "bad_request", "Invite code is required.")

    user = db.session.get(User, int(g.user_id))
    if not user:
        raise ApiError(401, "unauthorized", "Invalid token.")

    try:
        room = (
            Room.query.options(joinedload(Room.members))
            .filter_by(invite_code=invite_code)
            .one_or_none()
        )
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    if not room:
        raise ApiError(404, "not_found", "Room not found.")
    if room.status != RoomStatus.LOBBY:
        raise ApiError(409, "conflict", "Room is not joinable.")
    if room.locked:
        raise ApiError(403, "forbidden", "Room is locked.")

    try:
        existing_member = (
            RoomMember.query.filter_by(room_id=room.id, user_id=user.id, left_at=None).one_or_none()
        )
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    if existing_member:
        raise ApiError(409, "conflict", "You are already in this room.")

    if _active_participant_count(room) >= room.max_players:
        raise ApiError(409, "conflict", "Room is full.")

    db.session.add(
        RoomMember(
            room_id=room.id,
            user_id=user.id,
            role=RoomRole.PLAYER,
            ready=False,
        )
    )
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ApiError(409, "conflict", "Unable to join room.") from exc

    return jsonify({"id": str(room.id)}), 200


@bp.get("/rooms/<room_id>")
@auth_required
def get_room(room_id: str):
    try:
        room_id_int = int(room_id)
    except ValueError as exc:
        raise ApiError(404, "not_found", "Room not found.") from exc

    try:
        room = (
            Room.query.options(joinedload(Room.members).joinedload(RoomMember.user), joinedload(Room.puzzle_pack))
            .filter_by(id=room_id_int)
            .one_or_none()
        )
    except (OperationalError, ProgrammingError) as exc:
        db.session.rollback()
        raise ApiError(503, "service_unavailable", "Database not ready.") from exc
    if not room:
        raise ApiError(404, "not_found", "Room not found.")

    return jsonify(_room_payload(room)), 200


# Phase 7 scope ends at lobby. Keep placeholder routes stable for the current UI.
@bp.get("/rooms/<room_id>/tasks")
@auth_required
def get_tasks_placeholder(room_id: str):
    return jsonify([]), 200

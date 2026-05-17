from __future__ import annotations

import enum
from datetime import datetime

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class RoomStatus(str, enum.Enum):
    LOBBY = "LOBBY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class RoomRole(str, enum.Enum):
    OWNER = "OWNER"
    PLAYER = "PLAYER"
    SPECTATOR = "SPECTATOR"


class RoomTaskStatus(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(128), nullable=True)

    owned_rooms = db.relationship("Room", back_populates="owner", lazy="select")


class PuzzlePack(TimestampMixin, db.Model):
    __tablename__ = "puzzle_packs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True, index=True)
    genre = db.Column(db.String(64), nullable=False)
    difficulty = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text, nullable=True)
    estimated_minutes = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    tasks = db.relationship(
        "PuzzleTask",
        back_populates="puzzle_pack",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="PuzzleTask.order_index",
    )


class PuzzleTask(TimestampMixin, db.Model):
    __tablename__ = "puzzle_tasks"

    id = db.Column(db.Integer, primary_key=True)
    puzzle_pack_id = db.Column(db.Integer, db.ForeignKey("puzzle_packs.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    difficulty = db.Column(db.String(32), nullable=True)

    puzzle_pack = db.relationship("PuzzlePack", back_populates="tasks", lazy="select")


class Room(TimestampMixin, db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    puzzle_pack_id = db.Column(db.Integer, db.ForeignKey("puzzle_packs.id", ondelete="RESTRICT"), nullable=False, index=True)

    invite_code = db.Column(db.String(16), nullable=False, unique=True, index=True)
    status = db.Column(db.Enum(RoomStatus, name="room_status"), nullable=False, default=RoomStatus.LOBBY)
    max_players = db.Column(db.Integer, nullable=False, default=4)
    locked = db.Column(db.Boolean, nullable=False, default=False)
    owner_participates = db.Column(db.Boolean, nullable=False, default=True)

    started_at = db.Column(db.DateTime(timezone=True), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    owner = db.relationship("User", back_populates="owned_rooms", lazy="select")
    puzzle_pack = db.relationship("PuzzlePack", lazy="select")
    members = db.relationship("RoomMember", back_populates="room", cascade="all, delete-orphan", lazy="select")
    room_tasks = db.relationship("RoomTask", back_populates="room", cascade="all, delete-orphan", lazy="select")


class RoomMember(db.Model):
    __tablename__ = "room_members"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    role = db.Column(db.Enum(RoomRole, name="room_role"), nullable=False, default=RoomRole.PLAYER)
    ready = db.Column(db.Boolean, nullable=False, default=False)
    joined_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    left_at = db.Column(db.DateTime(timezone=True), nullable=True)

    room = db.relationship("Room", back_populates="members", lazy="select")
    user = db.relationship("User", lazy="select")

    __table_args__ = (
        db.UniqueConstraint("room_id", "user_id", name="uq_room_members_room_user"),
    )


class RoomTask(db.Model):
    __tablename__ = "room_tasks"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    puzzle_task_id = db.Column(db.Integer, db.ForeignKey("puzzle_tasks.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    status = db.Column(db.Enum(RoomTaskStatus, name="room_task_status"), nullable=False, default=RoomTaskStatus.ASSIGNED)
    submitted_answer = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime(timezone=True), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    room = db.relationship("Room", back_populates="room_tasks", lazy="select")
    puzzle_task = db.relationship("PuzzleTask", lazy="select")
    assigned_to = db.relationship("User", lazy="select")

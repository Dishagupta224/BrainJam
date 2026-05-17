import jwt

from app.extensions import db
from app.models import PuzzlePack, User


def _make_user(app, *, username, email):
    with app.app_context():
        user = User(username=username, email=email, password_hash="x", display_name=username)
        db.session.add(user)
        db.session.commit()
        return user.id


def _make_token(app, sub):
    secret = app.config["SECRET_KEY"]
    return jwt.encode({"sub": str(sub), "username": "u", "email": "e@example.com"}, secret, algorithm="HS256")


def _seed_puzzle(app, *, slug="clocktower"):
    with app.app_context():
        pack = PuzzlePack(
            title="Clocktower Cipher",
            slug=slug,
            genre="Cipher",
            difficulty="Medium",
            description="x",
            estimated_minutes=10,
            is_active=True,
        )
        db.session.add(pack)
        db.session.commit()


def test_create_room_requires_auth(client):
    res = client.post("/api/rooms", json={"puzzleId": "clocktower", "maxPlayers": 4, "ownerParticipates": True})
    assert res.status_code == 401


def test_create_and_join_room_lobby(client):
    _seed_puzzle(client.application, slug="clocktower")
    owner_id = _make_user(client.application, username="owner", email="owner@example.com")
    owner_token = _make_token(client.application, owner_id)

    create = client.post(
        "/api/rooms",
        json={"puzzleId": "clocktower", "maxPlayers": 4, "ownerParticipates": True},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert create.status_code == 200
    room = create.get_json()
    assert room["status"] == "LOBBY"
    assert room["maxPlayers"] == 4
    assert room["ownerId"] == owner_id
    assert isinstance(room["inviteCode"], str) and len(room["inviteCode"]) == 8
    assert len(room["members"]) == 1
    assert room["members"][0]["id"] == owner_id

    joiner_id = _make_user(client.application, username="joiner", email="joiner@example.com")
    joiner_token = _make_token(client.application, joiner_id)

    join = client.post(
        "/api/rooms/join",
        json={"inviteCode": room["inviteCode"]},
        headers={"Authorization": f"Bearer {joiner_token}"},
    )
    assert join.status_code == 200
    assert join.get_json()["id"] == room["id"]

    lobby = client.get(f"/api/rooms/{room['id']}", headers={"Authorization": f"Bearer {joiner_token}"})
    assert lobby.status_code == 200
    lobby_data = lobby.get_json()
    assert len(lobby_data["members"]) == 2


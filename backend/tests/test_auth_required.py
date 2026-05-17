import jwt

from app.extensions import db
from app.models import User


def _make_user(app, *, username="brainjammer", email="user@example.com", password_hash="x"):
    with app.app_context():
        user = User(username=username, email=email, password_hash=password_hash, display_name=username)
        db.session.add(user)
        db.session.commit()
        return user.id


def _make_token(app, sub="1"):
    secret = app.config["SECRET_KEY"]
    return jwt.encode({"sub": sub, "username": "u", "email": "e@example.com"}, secret, algorithm="HS256")


def test_auth_required_missing_token(client):
    res = client.get("/api/me")
    assert res.status_code == 401
    data = res.get_json()
    assert data["code"] == "unauthorized"


def test_auth_required_invalid_token(client):
    res = client.get("/api/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert res.status_code == 401
    data = res.get_json()
    assert data["code"] == "unauthorized"


def test_auth_required_valid_token(client):
    user_id = _make_user(client.application)
    token = _make_token(client.application, sub=str(user_id))
    res = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == user_id

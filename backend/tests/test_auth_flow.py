def test_register_login_me(client):
    reg = client.post(
        "/api/auth/register",
        json={"username": "BrainJammer", "email": "USER@EXAMPLE.COM", "password": "password123"},
    )
    assert reg.status_code == 200
    reg_data = reg.get_json()
    assert "token" in reg_data
    assert reg_data["user"]["username"] == "brainjammer"

    login = client.post(
        "/api/auth/login",
        json={"identifier": "user@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    login_data = login.get_json()
    assert "token" in login_data

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_data['token']}"})
    assert me.status_code == 200
    me_data = me.get_json()
    assert me_data["username"] == "brainjammer"


def test_register_validation(client):
    res = client.post("/api/auth/register", json={"username": "a", "email": "x@y.com", "password": "short"})
    assert res.status_code == 400
    data = res.get_json()
    assert data["code"] == "bad_request"

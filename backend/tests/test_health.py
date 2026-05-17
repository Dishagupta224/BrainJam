def test_health_ok(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.data.decode("utf-8") == "OK"

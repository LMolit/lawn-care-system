def test_login_is_rate_limited(client):
    for _ in range(10):
        client.post(
            "/api/v1/auth/login",
            json={"email": "a@example.com", "password": "wrong-password"},
        )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 429
    assert response.json()["error"] == "rate_limited"
    assert "retry-after" in response.headers

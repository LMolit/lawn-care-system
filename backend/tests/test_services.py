def test_create_service_returns_201(authed_client):
    response = authed_client.post(
        "/api/v1/services",
        json={
            "name": "Weekly Mowing",
            "description": "Standard mow, edge, blow",
            "base_price": 45.00,
            "estimated_duration_minutes": 30,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Weekly Mowing"
    assert body["base_price"] == 45.00
    assert body["id"] is not None


def test_list_services_requires_auth(client):
    response = client.get("/api/v1/services")
    assert response.status_code == 401


def test_create_service_missing_name_returns_422(authed_client):
    response = authed_client.post(
        "/api/v1/services",
        json={"base_price": 45.00, "estimated_duration_minutes": 30},
    )
    assert response.status_code == 422


def test_update_nonexistent_service_returns_404(authed_client):
    response = authed_client.patch(
        "/api/v1/services/999999", json={"base_price": 10.00}
    )
    assert response.status_code == 404


def test_list_services_shows_created_service(authed_client):
    create_response = authed_client.post(
        "/api/v1/services",
        json={
            "name": "Aeration",
            "description": None,
            "base_price": 175.00,
            "estimated_duration_minutes": 60,
        },
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    list_response = authed_client.get("/api/v1/services")
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == created_id


def test_update_service_price_preserves_other_fields(authed_client):
    create_response = authed_client.post(
        "/api/v1/services",
        json={
            "name": "Mulching",
            "description": "Spring mulch application",
            "base_price": 200.00,
            "estimated_duration_minutes": 90,
        },
    )
    assert create_response.status_code == 201
    service_id = create_response.json()["id"]

    update_response = authed_client.patch(
        f"/api/v1/services/{service_id}", json={"base_price": 225.00}
    )
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["base_price"] == 225.00
    assert body["name"] == "Mulching"
    assert body["description"] == "Spring mulch application"
    assert body["estimated_duration_minutes"] == 90

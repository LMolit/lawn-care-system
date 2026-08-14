def test_create_lead_returns_201(client):
    response = client.post(
        "/api/v1/leads",
        json={
            "name": "Test Person",
            "email": "test@example.com",
            "phone": "555-1234",
            "address": "123 Main St",
            "message": "Interested in weekly mowing",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "new"
    assert body["name"] == "Test Person"
    assert body["id"] is not None


def test_list_leads_requires_auth(client):
    response = client.get("/api/v1/leads")
    assert response.status_code == 401


def test_convert_requires_auth(client):
    response = client.post(
        "/api/v1/leads/00000000-0000-0000-0000-000000000000/convert",
    )
    assert response.status_code == 401


def test_convert_nonexistent_lead_returns_404(authed_client):
    response = authed_client.post(
        "/api/v1/leads/00000000-0000-0000-0000-000000000000/convert",
    )
    assert response.status_code == 404

def test_list_leads_shows_created_lead(authed_client):
    create_response = authed_client.post(
        "/api/v1/leads",
        json={
            "name": "List Test",
            "email": "list@example.com",
            "phone": None,
            "address": "1 List Way",
            "message": None,
        },
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    list_response = authed_client.get("/api/v1/leads")
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == created_id


def test_convert_lead_creates_customer(authed_client):
    create_response = authed_client.post(
        "/api/v1/leads",
        json={
            "name": "Convert Test",
            "email": "convert@example.com",
            "phone": "555-0000",
            "address": "1 Convert Way",
            "message": None,
        },
    )
    lead_id = create_response.json()["id"]

    convert_response = authed_client.post(f"/api/v1/leads/{lead_id}/convert")
    assert convert_response.status_code == 201
    body = convert_response.json()
    assert body["name"] == "Convert Test"
    assert body["lead_id"] == lead_id


def test_convert_already_converted_lead_returns_409(authed_client):
    create_response = authed_client.post(
        "/api/v1/leads",
        json={
            "name": "Double Convert",
            "email": None,
            "phone": None,
            "address": "1 Double Way",
            "message": None,
        },
    )
    lead_id = create_response.json()["id"]

    first = authed_client.post(f"/api/v1/leads/{lead_id}/convert")
    assert first.status_code == 201

    second = authed_client.post(f"/api/v1/leads/{lead_id}/convert")
    assert second.status_code == 409

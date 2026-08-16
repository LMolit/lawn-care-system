def test_create_customer_returns_201(authed_client):
    response = authed_client.post(
        "/api/v1/customers",
        json={
            "name": "Test Person",
            "email": "test@example.com",
            "phone": "555-9999",
            "notes": "No Notes",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["active"] is True
    assert body["name"] == "Test Person"
    assert body["id"] is not None

def test_list_customers_requires_auth(client):
    response = client.get("/api/v1/customers")
    assert response.status_code == 401

def test_update_customer_returns_201(authed_client):

    create_response = authed_client.post(
        "/api/v1/customers",
        json={
            "name": "Test Person",
            "email": "test@example.com",
            "phone": "555-9999",
            "notes": "No Notes",
        },
    )

    assert create_response.status_code == 201
    create_body = create_response.json()
    user_id = create_body["id"]

    update_response = authed_client.patch(f"/api/v1/customers/{user_id}", json={"phone": "000-0000"})

    assert update_response.status_code == 200
    update_body =  update_response.json()
    assert update_body["name"] == "Test Person"
    assert update_body["phone"] == "000-0000"

def test_list_customers_shows_created_customer(authed_client):
    created_response = authed_client.post(
        "/api/v1/customers",
        json={
            "name": "Test Person",
            "email": "test@example.com",
            "phone": "555-9999",
            "notes": None,
        },
    )

    assert created_response.status_code == 201
    created_id = created_response.json()["id"]

    list_response = authed_client.get("/api/v1/customers", params={"active": True})
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == created_id

def test_create_customer_missing_name_returns_422(authed_client):
    response = authed_client.post(
        "/api/v1/customers",
        json={"email": "test@example.com", "phone": "555-9999"},
    )
    assert response.status_code == 422

def test_update_nonexistent_customer_returns_404(authed_client):
    response = authed_client.patch("/api/v1/customers/999999", json={"phone": "555-0000"})
    assert response.status_code == 404

def test_create_customer_with_only_name(authed_client):
    response = authed_client.post("/api/v1/customers", json={"name": "Minimal Person"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] is None
    assert body["phone"] is None



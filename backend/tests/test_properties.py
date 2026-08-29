def test_create_property_returns_201(authed_client):
    customer_response = authed_client.post(
        "/api/v1/customers",
        json={"name": "Property Owner"},
    )
    customer_id = customer_response.json()["id"]

    response = authed_client.post(
        "/api/v1/properties",
        json={
            "customer_id": customer_id,
            "address": "42 Test Lane",
            "latitude": 41.5,
            "longitude": -87.5,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["address"] == "42 Test Lane"
    assert body["latitude"] == 41.5
    assert body["longitude"] == -87.5
    assert body["id"] is not None

def test_list_properties_requires_auth(client):
    response = client.get("/api/v1/properties")
    assert response.status_code == 401


def test_create_property_missing_address_returns_422(authed_client):
    response = authed_client.post(
        "/api/v1/properties",
        json={"customer_id": 1, "latitude": 41.5, "longitude": -87.5},
    )
    assert response.status_code == 422


def test_get_nonexistent_property_returns_404(authed_client):
    response = authed_client.get("/api/v1/properties/999999")
    assert response.status_code == 404


def test_update_nonexistent_property_returns_404(authed_client):
    response = authed_client.patch(
        "/api/v1/properties/999999", json={"latitude": 40.0}
    )
    assert response.status_code == 404


def test_list_properties_filters_by_customer(authed_client):
    customer_response = authed_client.post(
        "/api/v1/customers",
        json={"name": "Filter Owner"},
    )
    customer_id = customer_response.json()["id"]

    create_response = authed_client.post(
        "/api/v1/properties",
        json={
            "customer_id": customer_id,
            "address": "1 Filter Test Way",
            "latitude": 10.0,
            "longitude": 20.0,
        },
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    list_response = authed_client.get(
        "/api/v1/properties", params={"customer_id": customer_id}
    )
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == created_id

def test_update_property_latitude_preserves_other_fields(authed_client):
    customer_response = authed_client.post(
        "/api/v1/customers",
        json={"name": "Preserve Owner"},
    )
    customer_id = customer_response.json()["id"]

    create_response = authed_client.post(
        "/api/v1/properties",
        json={
            "customer_id": customer_id,
            "address": "9 Preserve Ave",
            "latitude": 5.0,
            "longitude": 6.0,
        },
    )
    assert create_response.status_code == 201
    property_id = create_response.json()["id"]

    update_response = authed_client.patch(
        f"/api/v1/properties/{property_id}", json={"latitude": 45.0}
    )
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["latitude"] == 45.0
    assert body["longitude"] == 6.0
    assert body["address"] == "9 Preserve Ave"

def test_create_property_invalid_latitude_returns_422(authed_client):
    customer_response = authed_client.post("/api/v1/customers", json={"name": "Bad Coord Owner"})
    customer_id = customer_response.json()["id"]

    response = authed_client.post(
        "/api/v1/properties",
        json={"customer_id": customer_id, "address": "1 Bad Way", "latitude": 99.0, "longitude": 0.0},
    )
    assert response.status_code == 422

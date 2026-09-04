from datetime import date, timedelta


def _create_customer_property_service(authed_client):
    """Helper: sets up a real customer, a property belonging to that customer,
    and a service — the minimum real data any job needs to reference."""
    customer_response = authed_client.post("/api/v1/customers", json={"name": "Job Test Customer"})
    customer_id = customer_response.json()["id"]

    property_response = authed_client.post(
        "/api/v1/properties",
        json={"customer_id": customer_id, "address": "1 Job Test Way", "latitude": 10.0, "longitude": 10.0},
    )
    property_id = property_response.json()["id"]

    service_response = authed_client.post(
        "/api/v1/services",
        json={"name": "Test Mow", "description": None, "base_price": 45.00, "estimated_duration_minutes": 30},
    )
    service_id = service_response.json()["id"]

    return customer_id, property_id, service_id


FUTURE_DATE = (date.today() + timedelta(days=30)).isoformat()


def test_create_job_returns_201(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)

    response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 45.00,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "scheduled"
    assert body["estimated_duration_minutes"] == 30  # pulled from the service, never sent explicitly
    assert body["id"] is not None


def test_list_jobs_requires_auth(client):
    response = client.get("/api/v1/jobs")
    assert response.status_code == 401


def test_create_job_mismatched_property_returns_400(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)

    other_customer_response = authed_client.post("/api/v1/customers", json={"name": "Other Customer"})
    other_customer_id = other_customer_response.json()["id"]

    response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": other_customer_id,
            "property_id": property_id,  # belongs to the FIRST customer, not this one
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 45.00,
        },
    )
    assert response.status_code == 400


def test_create_job_past_date_returns_422(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)

    response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": "2020-01-01",
            "price": 45.00,
        },
    )
    assert response.status_code == 422


def test_get_nonexistent_job_returns_404(authed_client):
    response = authed_client.get("/api/v1/jobs/999999")
    assert response.status_code == 404


def test_update_nonexistent_job_returns_404(authed_client):
    response = authed_client.patch("/api/v1/jobs/999999", json={"price": 10.00})
    assert response.status_code == 404


def test_list_jobs_filters_by_customer(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)

    create_response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 45.00,
        },
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    list_response = authed_client.get("/api/v1/jobs", params={"customer_id": customer_id})
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == created_id


def test_update_job_price_preserves_other_fields(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)

    create_response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 45.00,
            "notes": "Original notes",
        },
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["id"]

    update_response = authed_client.patch(f"/api/v1/jobs/{job_id}", json={"price": 60.00})
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["price"] == 60.00
    assert body["notes"] == "Original notes"
    assert body["status"] == "scheduled"

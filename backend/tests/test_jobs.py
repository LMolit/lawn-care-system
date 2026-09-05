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

def _create_scheduled_job(authed_client):
    """Helper: builds a full customer/property/service chain and a real
    scheduled job, returning its id for start/complete tests."""
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
    return response.json()["id"]


def test_start_job_sets_in_progress(authed_client):
    job_id = _create_scheduled_job(authed_client)

    response = authed_client.post(
        f"/api/v1/jobs/{job_id}/start",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T09:00:00Z"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_start_already_started_job_returns_409(authed_client):
    job_id = _create_scheduled_job(authed_client)

    first = authed_client.post(
        f"/api/v1/jobs/{job_id}/start",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T09:00:00Z"},
    )
    assert first.status_code == 200

    second = authed_client.post(
        f"/api/v1/jobs/{job_id}/start",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T09:05:00Z"},
    )
    assert second.status_code == 409


def test_complete_job_calculates_duration(authed_client):
    job_id = _create_scheduled_job(authed_client)

    authed_client.post(
        f"/api/v1/jobs/{job_id}/start",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T09:00:00Z"},
    )

    response = authed_client.post(
        f"/api/v1/jobs/{job_id}/complete",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T09:45:00Z"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["actual_duration_minutes"] == 45


def test_complete_job_without_starting_returns_409(authed_client):
    job_id = _create_scheduled_job(authed_client)

    response = authed_client.post(
        f"/api/v1/jobs/{job_id}/complete",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T09:45:00Z"},
    )
    assert response.status_code == 409


def test_complete_already_completed_job_returns_409(authed_client):
    job_id = _create_scheduled_job(authed_client)

    authed_client.post(
        f"/api/v1/jobs/{job_id}/start",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T09:00:00Z"},
    )
    first_complete = authed_client.post(
        f"/api/v1/jobs/{job_id}/complete",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T09:45:00Z"},
    )
    assert first_complete.status_code == 200

    second_complete = authed_client.post(
        f"/api/v1/jobs/{job_id}/complete",
        json={"latitude": 41.5, "longitude": -87.5, "timestamp": "2026-09-05T10:00:00Z"},
    )
    assert second_complete.status_code == 409

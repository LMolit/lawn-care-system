from tests.test_jobs import _create_customer_property_service, FUTURE_DATE

def test_create_invoice_returns_201(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)
    job_response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 45.00,
        },
    )
    job_id = job_response.json()["id"]
    authed_client.post(f"/api/v1/jobs/{job_id}/start", json={"latitude": 1.0, "longitude": 1.0, "timestamp": "2026-09-09T09:00:00Z"})
    authed_client.post(f"/api/v1/jobs/{job_id}/complete", json={"latitude": 1.0, "longitude": 1.0, "timestamp": "2026-09-09T09:45:00Z"})

    response = authed_client.post(
        "/api/v1/invoices",
        json={"customer_id": customer_id, "job_ids": [job_id], "due_date": "2027-01-01"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["total"] == 45.0
    assert len(body["line_items"]) == 1
    assert body["line_items"][0]["job_id"] == job_id


def test_create_invoice_uncompleted_job_returns_422_or_400(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)
    job_response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 45.00,
        },
    )
    job_id = job_response.json()["id"]
    # never started or completed — still "scheduled"

    response = authed_client.post(
        "/api/v1/invoices",
        json={"customer_id": customer_id, "job_ids": [job_id], "due_date": "2027-01-01"},
    )
    assert response.status_code == 400


def test_create_invoice_same_job_twice_returns_409(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)
    job_response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 45.00,
        },
    )
    job_id = job_response.json()["id"]
    authed_client.post(f"/api/v1/jobs/{job_id}/start", json={"latitude": 1.0, "longitude": 1.0, "timestamp": "2026-09-09T09:00:00Z"})
    authed_client.post(f"/api/v1/jobs/{job_id}/complete", json={"latitude": 1.0, "longitude": 1.0, "timestamp": "2026-09-09T09:45:00Z"})

    first = authed_client.post(
        "/api/v1/invoices",
        json={"customer_id": customer_id, "job_ids": [job_id], "due_date": "2027-01-01"},
    )
    assert first.status_code == 201

    second = authed_client.post(
        "/api/v1/invoices",
        json={"customer_id": customer_id, "job_ids": [job_id], "due_date": "2027-01-01"},
    )
    assert second.status_code == 409


def test_create_invoice_requires_auth(client):
    response = client.post("/api/v1/invoices", json={"customer_id": 1, "job_ids": [1], "due_date": "2027-01-01"})
    assert response.status_code == 401

def test_send_invoice_marks_as_sent(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)
    authed_client.patch(f"/api/v1/customers/{customer_id}", json={"email": "ronin.molitor@gmail.com"})

    job_response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 45.00,
        },
    )
    job_id = job_response.json()["id"]
    authed_client.post(f"/api/v1/jobs/{job_id}/start", json={"latitude": 1.0, "longitude": 1.0, "timestamp": "2026-09-09T09:00:00Z"})
    authed_client.post(f"/api/v1/jobs/{job_id}/complete", json={"latitude": 1.0, "longitude": 1.0, "timestamp": "2026-09-09T09:45:00Z"})

    invoice_response = authed_client.post(
        "/api/v1/invoices",
        json={"customer_id": customer_id, "job_ids": [job_id], "due_date": "2027-01-01"},
    )
    invoice_id = invoice_response.json()["id"]

    response = authed_client.post(f"/api/v1/invoices/{invoice_id}/send")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "sent"
    assert body["sent_at"] is not None


def test_send_invoice_requires_auth(client):
    response = client.post("/api/v1/invoices/1/send")
    assert response.status_code == 401

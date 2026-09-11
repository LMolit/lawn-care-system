from tests.test_jobs import _create_customer_property_service, FUTURE_DATE

def test_create_payment_on_draft_invoice_returns_400(authed_client):
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

    invoice_response = authed_client.post(
        "/api/v1/invoices",
        json={"customer_id": customer_id, "job_ids": [job_id], "due_date": "2027-01-01"},
    )
    invoice_id = invoice_response.json()["id"]
    # never sent — still "draft"

    response = authed_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_id, "amount": 10.00, "method": "cash", "paid_at": "2026-09-11T10:00:00Z"},
    )
    assert response.status_code == 400


def test_full_payment_marks_invoice_paid(authed_client):
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
    authed_client.post(f"/api/v1/invoices/{invoice_id}/send")

    partial = authed_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_id, "amount": 20.00, "method": "cash", "paid_at": "2026-09-11T10:00:00Z"},
    )
    assert partial.status_code == 201

    still_sent = authed_client.get(f"/api/v1/invoices/{invoice_id}")
    assert still_sent.json()["status"] == "sent"

    final = authed_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_id, "amount": 25.00, "method": "card", "paid_at": "2026-09-11T11:00:00Z"},
    )
    assert final.status_code == 201

    now_paid = authed_client.get(f"/api/v1/invoices/{invoice_id}")
    assert now_paid.json()["status"] == "paid"


def test_create_payment_requires_auth(client):
    response = client.post("/api/v1/payments", json={"invoice_id": 1, "amount": 10.00, "method": "cash", "paid_at": "2026-09-11T10:00:00Z"})
    assert response.status_code == 401

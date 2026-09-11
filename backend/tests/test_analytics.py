from tests.test_jobs import _create_customer_property_service, FUTURE_DATE

def test_get_overview_requires_auth(client):
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 401


def test_get_overview_returns_expected_shape(authed_client):
    response = authed_client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    body = response.json()
    assert "revenue_this_month" in body
    assert "jobs_completed_this_month" in body
    assert "active_customers" in body
    assert "avg_job_duration_minutes" in body


def test_profit_loss_matches_revenue_and_expenses(authed_client, db_session):
    from app.db.base import ExpenseCategory
    category = ExpenseCategory(name="Test PL Category")
    db_session.add(category)
    db_session.commit()

    authed_client.post(
        "/api/v1/expenses",
        json={"category_id": category.id, "description": "Test expense", "amount": 30.00, "date": "2026-09-11"},
    )

    customer_id, property_id, service_id = _create_customer_property_service(authed_client)
    job_response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": FUTURE_DATE,
            "price": 100.00,
        },
    )
    job_id = job_response.json()["id"]
    authed_client.post(f"/api/v1/jobs/{job_id}/start", json={"latitude": 1.0, "longitude": 1.0, "timestamp": "2026-09-09T09:00:00Z"})
    authed_client.post(f"/api/v1/jobs/{job_id}/complete", json={"latitude": 1.0, "longitude": 1.0, "timestamp": "2026-09-09T09:45:00Z"})
    authed_client.post(
        "/api/v1/invoices",
        json={"customer_id": customer_id, "job_ids": [job_id], "due_date": "2027-01-01"},
    )

    response = authed_client.get("/api/v1/analytics/profit-loss?start_date=2026-09-01&end_date=2026-09-30")
    assert response.status_code == 200
    body = response.json()
    assert body["revenue"] == 100.0
    assert body["expenses"] == 30.0
    assert body["profit"] == 70.0

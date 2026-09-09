from tests.test_jobs import _create_customer_property_service

def test_generate_route_creates_empty_route_for_no_jobs(authed_client):
    response = authed_client.post(
        "/api/v1/routes/generate",
        json={"date": "2027-06-01"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["stops"] == []
    assert body["algorithm_used"] == "nearest_neighbor_v1"


def test_generate_route_with_one_job(authed_client):
    customer_id, property_id, service_id = _create_customer_property_service(authed_client)
    job_response = authed_client.post(
        "/api/v1/jobs",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "service_id": service_id,
            "scheduled_date": "2027-06-02",
            "price": 45.00,
        },
    )
    job_id = job_response.json()["id"]

    response = authed_client.post(
        "/api/v1/routes/generate",
        json={"date": "2027-06-02"},
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["stops"]) == 1
    assert body["stops"][0]["job_id"] == job_id
    assert body["stops"][0]["sequence_order"] == 1


def test_get_todays_route_returns_404_when_none_exists(client, authed_client):
    response = authed_client.get("/api/v1/routes/today")
    assert response.status_code == 404

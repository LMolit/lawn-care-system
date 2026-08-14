def test_create_review_defaults_to_unapproved(client):
    response = client.post(
        "/api/v1/reviews",
        json={"name": "Jane Homeowner", "rating": 5, "comment": "Great work"},
    )
    assert response.status_code == 201
    assert response.json()["approved"] is False


def test_create_review_invalid_rating_returns_422(client):
    response = client.post(
        "/api/v1/reviews",
        json={"name": "Bad Rating", "rating": 8, "comment": "should fail"},
    )
    assert response.status_code == 422


def test_list_reviews_excludes_unapproved(client):
    client.post(
        "/api/v1/reviews",
        json={"name": "Unapproved Person", "rating": 4, "comment": None},
    )
    response = client.get("/api/v1/reviews")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_approve_review_requires_auth(client):
    response = client.patch(
        "/api/v1/reviews/00000000-0000-0000-0000-000000000000/approve",
        json={"approved": True},
    )
    assert response.status_code == 401


def test_approve_nonexistent_review_returns_404(authed_client):
    response = authed_client.patch(
        "/api/v1/reviews/00000000-0000-0000-0000-000000000000/approve",
        json={"approved": True},
    )
    assert response.status_code == 404


def test_approve_review_makes_it_visible(authed_client):
    create_response = authed_client.post(
        "/api/v1/reviews",
        json={"name": "Soon Approved", "rating": 5, "comment": None},
    )
    review_id = create_response.json()["id"]

    approve_response = authed_client.patch(
        f"/api/v1/reviews/{review_id}/approve",
        json={"approved": True},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["approved"] is True

    list_response = authed_client.get("/api/v1/reviews")
    assert list_response.json()["total"] == 1

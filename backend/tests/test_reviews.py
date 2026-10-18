import itertools

NO_SUCH_REVIEW = "00000000-0000-0000-0000-000000000000"
REVIEW = {"name": "Jane Homeowner", "rating": 5, "comment": "Great work"}

_visitor = itertools.count(1)


def _submit(client, name="Jane Homeowner", rating=5, comment="Great work"):
    # A fresh visitor address per call, so the per-IP rate limit never gets in the way.
    n = next(_visitor)
    response = client.post(
        "/api/v1/reviews",
        headers={"cf-connecting-ip": f"10.9.{n // 250}.{n % 250 + 1}"},
        json={"name": name, "rating": rating, "comment": comment},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _set_status(client, review_id, status):
    return client.patch(f"/api/v1/reviews/{review_id}", json={"status": status})


# Note: no test checks ordering. Postgres now() is constant inside one transaction,
# and each test runs in a single transaction, so every created_at ties.


# --- the public side (must not change) ---


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
    _submit(client)
    response = client.get("/api/v1/reviews")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_public_list_shows_only_approved_reviews(authed_client):
    approved = _submit(authed_client, name="Approved Person")
    hidden = _submit(authed_client, name="Hidden Person")
    _submit(authed_client, name="Pending Person")
    _set_status(authed_client, approved, "approved")
    _set_status(authed_client, hidden, "hidden")

    body = authed_client.get("/api/v1/reviews").json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Approved Person"
    assert body["items"][0]["approved"] is True


# --- the moderation endpoints require a login ---


def test_moderation_list_requires_auth(client):
    assert client.get("/api/v1/reviews/admin").status_code == 401


def test_moderation_counts_require_auth(client):
    assert client.get("/api/v1/reviews/admin/counts").status_code == 401


def test_changing_status_requires_auth(client):
    assert _set_status(client, NO_SUCH_REVIEW, "approved").status_code == 401


# --- the moderation list ---


def test_moderation_list_shows_every_status_by_default(authed_client):
    approved = _submit(authed_client, name="A")
    hidden = _submit(authed_client, name="B")
    _submit(authed_client, name="C")
    _set_status(authed_client, approved, "approved")
    _set_status(authed_client, hidden, "hidden")

    body = authed_client.get("/api/v1/reviews/admin").json()
    assert body["total"] == 3
    assert {item["status"] for item in body["items"]} == {
        "pending",
        "approved",
        "hidden",
    }


def test_moderation_list_filters_by_status(authed_client):
    _submit(authed_client, name="Waiting")
    approved = _submit(authed_client, name="Live")
    _set_status(authed_client, approved, "approved")

    body = authed_client.get("/api/v1/reviews/admin?status=pending").json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Waiting"
    assert body["items"][0]["status"] == "pending"


def test_moderation_list_rejects_an_unknown_status(authed_client):
    assert authed_client.get("/api/v1/reviews/admin?status=spam").status_code == 422


def test_moderation_list_validates_paging(authed_client):
    assert authed_client.get("/api/v1/reviews/admin?page=0").status_code == 422
    assert authed_client.get("/api/v1/reviews/admin?page_size=101").status_code == 422


def test_moderation_list_paginates(authed_client):
    for name in ("A", "B", "C"):
        _submit(authed_client, name=name)

    first = authed_client.get("/api/v1/reviews/admin?page=1&page_size=2").json()
    second = authed_client.get("/api/v1/reviews/admin?page=2&page_size=2").json()
    assert first["total"] == 3 and len(first["items"]) == 2
    assert second["total"] == 3 and len(second["items"]) == 1


# --- the counts for the tab badges ---


def test_counts_are_zero_when_there_are_no_reviews(authed_client):
    response = authed_client.get("/api/v1/reviews/admin/counts")
    assert response.status_code == 200
    assert response.json() == {"pending": 0, "approved": 0, "hidden": 0}


def test_counts_group_reviews_by_status(authed_client):
    approved = _submit(authed_client, name="A")
    hidden = _submit(authed_client, name="B")
    _submit(authed_client, name="C")
    _submit(authed_client, name="D")
    _set_status(authed_client, approved, "approved")
    _set_status(authed_client, hidden, "hidden")

    response = authed_client.get("/api/v1/reviews/admin/counts")
    assert response.json() == {"pending": 2, "approved": 1, "hidden": 1}


# --- changing a review's status ---


def test_changing_the_status_of_a_missing_review_returns_404(authed_client):
    response = _set_status(authed_client, NO_SUCH_REVIEW, "approved")
    assert response.status_code == 404
    # Our own 404 shape, not the framework's "route not found"
    assert response.json()["error"] == "not_found"


def test_changing_status_rejects_an_unknown_value(authed_client):
    review_id = _submit(authed_client)
    assert _set_status(authed_client, review_id, "spam").status_code == 422


def test_approving_a_review_makes_it_public(authed_client):
    review_id = _submit(authed_client)
    response = _set_status(authed_client, review_id, "approved")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert authed_client.get("/api/v1/reviews").json()["total"] == 1


def test_hiding_an_approved_review_removes_it_from_the_public_list(authed_client):
    review_id = _submit(authed_client)
    _set_status(authed_client, review_id, "approved")
    response = _set_status(authed_client, review_id, "hidden")
    assert response.json()["status"] == "hidden"
    assert authed_client.get("/api/v1/reviews").json()["total"] == 0


def test_a_hidden_review_can_be_put_back_in_the_queue(authed_client):
    review_id = _submit(authed_client)
    _set_status(authed_client, review_id, "hidden")
    response = _set_status(authed_client, review_id, "pending")
    assert response.json()["status"] == "pending"
    assert authed_client.get("/api/v1/reviews/admin/counts").json()["pending"] == 1


def test_submitting_reviews_is_rate_limited_per_visitor(client):
    for _ in range(3):
        assert client.post("/api/v1/reviews", json=REVIEW).status_code == 201
    response = client.post("/api/v1/reviews", json=REVIEW)
    assert response.status_code == 429
    assert response.json()["error"] == "rate_limited"
    assert "retry-after" in response.headers


def test_one_visitors_limit_does_not_block_another(client):
    first_visitor = {"cf-connecting-ip": "203.0.113.1"}
    for _ in range(3):
        client.post("/api/v1/reviews", json=REVIEW, headers=first_visitor)

    blocked = client.post("/api/v1/reviews", json=REVIEW, headers=first_visitor)
    other = client.post(
        "/api/v1/reviews", json=REVIEW, headers={"cf-connecting-ip": "203.0.113.2"}
    )
    assert blocked.status_code == 429
    assert other.status_code == 201

def test_create_expense_returns_201(authed_client, db_session):
    from app.db.base import ExpenseCategory
    category = ExpenseCategory(name="Test Category")
    db_session.add(category)
    db_session.commit()

    response = authed_client.post(
        "/api/v1/expenses",
        json={"category_id": category.id, "description": "Gas", "amount": 45.50, "date": "2026-09-11", "vendor": "Shell"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["description"] == "Gas"
    assert body["amount"] == 45.50
    assert body["id"] is not None


def test_list_expenses_requires_auth(client):
    response = client.get("/api/v1/expenses")
    assert response.status_code == 401


def test_get_nonexistent_expense_returns_404(authed_client):
    response = authed_client.get("/api/v1/expenses/999999")
    assert response.status_code == 404


def test_update_nonexistent_expense_returns_404(authed_client):
    response = authed_client.patch("/api/v1/expenses/999999", json={"amount": 10.00})
    assert response.status_code == 404


def test_update_expense_amount_preserves_other_fields(authed_client, db_session):
    from app.db.base import ExpenseCategory
    category = ExpenseCategory(name="Preserve Category")
    db_session.add(category)
    db_session.commit()

    create_response = authed_client.post(
        "/api/v1/expenses",
        json={"category_id": category.id, "description": "Mulch supplies", "amount": 100.00, "date": "2026-09-11", "vendor": "Home Depot"},
    )
    expense_id = create_response.json()["id"]

    update_response = authed_client.patch(f"/api/v1/expenses/{expense_id}", json={"amount": 120.00})
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["amount"] == 120.00
    assert body["description"] == "Mulch supplies"
    assert body["vendor"] == "Home Depot"

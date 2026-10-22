import uuid

import pytest
import resend

from app.core.config import settings
from app.db.base import Lead
from app.services import email as email_service

OWNER = "owner-alerts@example.com"
LEAD = {"name": "Alert Person", "address": "1 Alert Way"}
REVIEW = {"name": "Alert Reviewer", "rating": 5, "comment": "Great work"}


@pytest.fixture()
def sent(monkeypatch):
    """Replaces the real Resend call. Tests never send real email."""
    messages = []
    monkeypatch.setattr(resend.Emails, "send", lambda params: messages.append(params))
    return messages


@pytest.fixture()
def alerts_on(monkeypatch):
    monkeypatch.setattr(settings, "owner_alert_email", OWNER)
    monkeypatch.setattr(
        settings, "site_url", "https://site.test/"
    )  # trailing slash on purpose


def test_a_new_lead_sends_the_owner_an_alert(client, alerts_on, sent):
    response = client.post("/api/v1/leads", json=LEAD)
    assert response.status_code == 201
    lead_id = response.json()["id"]

    assert len(sent) == 1
    message = sent[0]
    assert message["to"] == OWNER
    assert message["subject"] == "New quote request"
    assert f"https://site.test/admin/leads/{lead_id}" in message["text"]


def test_the_lead_alert_contains_nothing_the_customer_wrote(client, alerts_on, sent):
    client.post(
        "/api/v1/leads", json={**LEAD, "message": "Click http://evil.example now"}
    )
    message = sent[0]
    everything = message["subject"] + message["text"]
    assert "Alert Person" not in everything
    assert "1 Alert Way" not in everything
    assert "evil.example" not in everything


def test_alerts_are_plain_text_only(client, alerts_on, sent):
    client.post("/api/v1/leads", json=LEAD)
    assert "html" not in sent[0]
    assert sent[0]["text"]


def test_no_alert_is_sent_when_no_address_is_configured(client, monkeypatch, sent):
    monkeypatch.setattr(settings, "owner_alert_email", "")
    assert client.post("/api/v1/leads", json=LEAD).status_code == 201
    assert sent == []


def test_a_rejected_submission_sends_no_alert(client, alerts_on, sent):
    assert (
        client.post("/api/v1/leads", json={"address": "1 No Name Way"}).status_code
        == 422
    )
    assert sent == []


def test_a_failing_email_service_never_loses_the_lead(
    client, alerts_on, monkeypatch, db_session
):
    def explode(params):
        raise RuntimeError("resend is down")

    monkeypatch.setattr(resend.Emails, "send", explode)
    assert client.post("/api/v1/leads", json=LEAD).status_code == 201
    assert db_session.query(Lead).count() == 1


def test_a_new_review_sends_the_owner_an_alert(client, alerts_on, sent):
    assert client.post("/api/v1/reviews", json=REVIEW).status_code == 201
    assert len(sent) == 1
    message = sent[0]
    assert message["to"] == OWNER
    assert message["subject"] == "New review to moderate"
    assert "https://site.test/admin/reviews?status=pending" in message["text"]
    everything = message["subject"] + message["text"]
    assert "Alert Reviewer" not in everything
    assert "Great work" not in everything


def test_alerts_are_capped_per_hour_to_protect_the_email_quota(alerts_on, sent):
    for _ in range(email_service.ALERTS_PER_HOUR + 5):
        email_service.notify_new_lead(uuid.uuid4())
    assert len(sent) == email_service.ALERTS_PER_HOUR

import pytest

from app.db.base import Lead, LeadStatus

NO_SUCH_LEAD = "00000000-0000-0000-0000-000000000000"


def _lead(
    db_session,
    *,
    name="Lead Person",
    email=None,
    phone=None,
    address="1 Lead Way",
    status=LeadStatus.new,
):
    # Straight into the database: the public endpoint is rate limited, and these
    # tests are about the admin side, not about submitting leads.
    lead = Lead(name=name, email=email, phone=phone, address=address, status=status)
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


def _patch(client, lead_id, body):
    return client.patch(f"/api/v1/leads/{lead_id}", json=body)


# --- everything here needs a login ---


def test_getting_one_lead_requires_auth(client, db_session):
    lead = _lead(db_session)
    assert client.get(f"/api/v1/leads/{lead.id}").status_code == 401


def test_updating_a_lead_requires_auth(client, db_session):
    lead = _lead(db_session)
    assert _patch(client, lead.id, {"status": "contacted"}).status_code == 401


def test_counts_require_auth(client):
    assert client.get("/api/v1/leads/counts").status_code == 401


# --- one lead ---


def test_one_lead_includes_the_internal_notes_field(authed_client, db_session):
    lead = _lead(db_session, name="Detail Person")
    body = authed_client.get(f"/api/v1/leads/{lead.id}").json()
    assert body["name"] == "Detail Person"
    assert body["notes"] is None


def test_a_missing_lead_is_a_404_in_our_own_shape(authed_client):
    response = authed_client.get(f"/api/v1/leads/{NO_SUCH_LEAD}")
    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_updating_a_missing_lead_is_a_404(authed_client):
    assert (
        _patch(authed_client, NO_SUCH_LEAD, {"status": "contacted"}).status_code == 404
    )


def test_the_public_response_never_shows_internal_notes(client):
    response = client.post(
        "/api/v1/leads", json={"name": "Public Person", "address": "1 Public Way"}
    )
    assert response.status_code == 201
    assert "notes" not in response.json()


# --- counts ---


def test_counts_start_at_zero(authed_client):
    response = authed_client.get("/api/v1/leads/counts")
    assert response.status_code == 200
    assert response.json() == {
        "new": 0,
        "contacted": 0,
        "quoted": 0,
        "converted": 0,
        "lost": 0,
    }


def test_counts_group_leads_by_status(authed_client, db_session):
    _lead(db_session, name="A")
    _lead(db_session, name="B")
    _lead(db_session, name="C", status=LeadStatus.contacted)
    _lead(db_session, name="D", status=LeadStatus.lost)
    body = authed_client.get("/api/v1/leads/counts").json()
    assert body == {"new": 2, "contacted": 1, "quoted": 0, "converted": 0, "lost": 1}


# --- changing the status ---


@pytest.mark.parametrize("status", ["contacted", "quoted", "lost"])
def test_a_lead_can_be_moved_through_the_pipeline(authed_client, db_session, status):
    lead = _lead(db_session)
    response = _patch(authed_client, lead.id, {"status": status})
    assert response.status_code == 200
    assert response.json()["status"] == status
    assert authed_client.get(f"/api/v1/leads/{lead.id}").json()["status"] == status


def test_a_lead_can_be_set_back_to_new(authed_client, db_session):
    lead = _lead(db_session, status=LeadStatus.lost)
    assert _patch(authed_client, lead.id, {"status": "new"}).json()["status"] == "new"


def test_converted_cannot_be_set_through_the_update_endpoint(authed_client, db_session):
    lead = _lead(db_session)
    assert _patch(authed_client, lead.id, {"status": "converted"}).status_code == 422
    db_session.refresh(lead)
    assert lead.status == LeadStatus.new


def test_an_unknown_status_is_rejected(authed_client, db_session):
    lead = _lead(db_session)
    assert _patch(authed_client, lead.id, {"status": "spam"}).status_code == 422


def test_the_status_of_a_converted_lead_is_locked(authed_client, db_session):
    lead = _lead(db_session, status=LeadStatus.converted)
    response = _patch(authed_client, lead.id, {"status": "lost"})
    assert response.status_code == 409
    db_session.refresh(lead)
    assert lead.status == LeadStatus.converted


def test_notes_on_a_converted_lead_can_still_be_edited(authed_client, db_session):
    lead = _lead(db_session, status=LeadStatus.converted)
    response = _patch(authed_client, lead.id, {"notes": "Signed the contract"})
    assert response.status_code == 200
    assert response.json()["notes"] == "Signed the contract"


# --- internal notes ---


def test_notes_can_be_saved(authed_client, db_session):
    lead = _lead(db_session)
    response = _patch(authed_client, lead.id, {"notes": "Called, left a message"})
    assert response.status_code == 200
    assert response.json()["notes"] == "Called, left a message"
    assert (
        authed_client.get(f"/api/v1/leads/{lead.id}").json()["notes"]
        == "Called, left a message"
    )


@pytest.mark.parametrize("clearing_value", ["", None])
def test_notes_can_be_cleared(authed_client, db_session, clearing_value):
    lead = _lead(db_session)
    _patch(authed_client, lead.id, {"notes": "Something to remove"})
    response = _patch(authed_client, lead.id, {"notes": clearing_value})
    assert response.status_code == 200
    assert response.json()["notes"] is None


def test_notes_are_trimmed_and_whitespace_only_notes_are_cleared(
    authed_client, db_session
):
    lead = _lead(db_session)
    assert (
        _patch(authed_client, lead.id, {"notes": "  padded  "}).json()["notes"]
        == "padded"
    )
    assert _patch(authed_client, lead.id, {"notes": "     "}).json()["notes"] is None


def test_changing_the_status_does_not_touch_the_notes(authed_client, db_session):
    lead = _lead(db_session)
    _patch(authed_client, lead.id, {"notes": "Keep me"})
    response = _patch(authed_client, lead.id, {"status": "quoted"})
    assert response.json()["notes"] == "Keep me"


def test_overlong_notes_are_rejected(authed_client, db_session):
    lead = _lead(db_session)
    assert _patch(authed_client, lead.id, {"notes": "x" * 2001}).status_code == 422


def test_an_empty_update_changes_nothing(authed_client, db_session):
    lead = _lead(db_session, status=LeadStatus.quoted)
    response = _patch(authed_client, lead.id, {})
    assert response.status_code == 200
    assert response.json()["status"] == "quoted"


# --- the list ---


def test_the_list_includes_notes(authed_client, db_session):
    lead = _lead(db_session)
    _patch(authed_client, lead.id, {"notes": "Listed note"})
    items = authed_client.get("/api/v1/leads").json()["items"]
    assert items[0]["notes"] == "Listed note"


@pytest.mark.parametrize("params", [{"page": 0}, {"page_size": 0}, {"page_size": 101}])
def test_the_list_rejects_nonsense_paging(authed_client, params):
    assert authed_client.get("/api/v1/leads", params=params).status_code == 422


def test_the_list_filters_by_status(authed_client, db_session):
    _lead(db_session, name="Fresh")
    _lead(db_session, name="Contacted One", status=LeadStatus.contacted)
    body = authed_client.get("/api/v1/leads", params={"status": "contacted"}).json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Contacted One"


# --- search ---


def _names(client, **params):
    return sorted(
        item["name"]
        for item in client.get("/api/v1/leads", params=params).json()["items"]
    )


def test_search_finds_a_name_ignoring_case(authed_client, db_session):
    _lead(db_session, name="Margaret Thompson")
    _lead(db_session, name="Someone Else")
    assert _names(authed_client, q="margaret") == ["Margaret Thompson"]
    assert _names(authed_client, q="THOMPSON") == ["Margaret Thompson"]


def test_search_finds_an_email(authed_client, db_session):
    _lead(db_session, name="Emailer", email="findme@example.com")
    _lead(db_session, name="Other", email="other@example.com")
    assert _names(authed_client, q="findme@") == ["Emailer"]


def test_search_finds_part_of_a_phone_number(authed_client, db_session):
    _lead(db_session, name="Phoner", phone="(630) 555-0142")
    _lead(db_session, name="Other", phone="(630) 555-0999")
    assert _names(authed_client, q="0142") == ["Phoner"]


def test_search_finds_an_address(authed_client, db_session):
    _lead(db_session, name="Addressed", address="742 Evergreen Terrace")
    _lead(db_session, name="Other", address="1 Other Way")
    assert _names(authed_client, q="evergreen") == ["Addressed"]


def test_search_with_no_match_returns_an_empty_list(authed_client, db_session):
    _lead(db_session)
    body = authed_client.get("/api/v1/leads", params={"q": "zzzz-no-match"}).json()
    assert body["items"] == []
    assert body["total"] == 0


@pytest.mark.parametrize("wildcard", ["%", "_"])
def test_search_treats_wildcard_characters_as_plain_text(
    authed_client, db_session, wildcard
):
    _lead(db_session, name="Plain Name")
    assert _names(authed_client, q=wildcard) == []


def test_search_combines_with_the_status_filter(authed_client, db_session):
    _lead(db_session, name="Smith New")
    _lead(db_session, name="Smith Contacted", status=LeadStatus.contacted)
    assert _names(authed_client, q="smith", status="contacted") == ["Smith Contacted"]


def test_a_blank_search_returns_everything(authed_client, db_session):
    _lead(db_session, name="One")
    _lead(db_session, name="Two")
    assert _names(authed_client, q="   ") == ["One", "Two"]


def test_an_overlong_search_is_rejected(authed_client):
    assert (
        authed_client.get("/api/v1/leads", params={"q": "x" * 101}).status_code == 422
    )

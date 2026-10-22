import pytest

from app.db.base import Customer, Lead, LeadStatus, Property

# The same point the geocoder returned for Batavia's city hall. Longitude is the negative one.
LOCATION = {
    "address": "100 North Island Avenue, Batavia, IL, USA",
    "latitude": 41.851886,
    "longitude": -88.308163,
}


def _lead(db_session, name="Convert Person"):
    # Straight into the database: the public endpoint is rate limited, and
    # these tests are about conversion, not about submitting leads.
    lead = Lead(
        name=name, email="convert@example.com", phone="555-0100", address="1 Lead Way"
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


def _convert(client, lead_id, body=None):
    url = f"/api/v1/leads/{lead_id}/convert"
    return client.post(url, json=body) if body is not None else client.post(url)


def test_converting_without_a_location_creates_only_the_customer(
    authed_client, db_session
):
    lead = _lead(db_session)
    response = _convert(authed_client, lead.id)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Convert Person"
    assert body["property_id"] is None
    assert db_session.query(Property).count() == 0


def test_converting_with_a_location_creates_the_property_too(authed_client, db_session):
    lead = _lead(db_session)
    response = _convert(authed_client, lead.id, {"location": LOCATION})
    assert response.status_code == 201
    body = response.json()
    assert body["property_id"] is not None

    prop = authed_client.get(f"/api/v1/properties/{body['property_id']}").json()
    assert prop["customer_id"] == body["id"]
    assert prop["address"] == LOCATION["address"]
    # Both checked, so a swapped latitude and longitude cannot slip through
    assert prop["latitude"] == pytest.approx(LOCATION["latitude"])
    assert prop["longitude"] == pytest.approx(LOCATION["longitude"])


def test_conversion_links_the_lead_and_the_customer(authed_client, db_session):
    lead = _lead(db_session)
    body = _convert(authed_client, lead.id, {"location": LOCATION}).json()
    db_session.refresh(lead)
    assert lead.status == LeadStatus.converted
    assert lead.converted_customer_id == body["id"]
    assert body["lead_id"] == str(lead.id)


@pytest.mark.parametrize(
    "location",
    [
        {**LOCATION, "latitude": 95},
        {**LOCATION, "longitude": -181},
        {"address": LOCATION["address"]},  # no coordinates at all
        {**LOCATION, "address": "   "},  # blank once trimmed
    ],
)
def test_a_bad_location_is_rejected_and_nothing_is_created(
    authed_client, db_session, location
):
    lead = _lead(db_session)
    assert _convert(authed_client, lead.id, {"location": location}).status_code == 422
    assert db_session.query(Customer).count() == 0
    assert db_session.get(Lead, lead.id).status == LeadStatus.new


def test_converting_with_a_location_requires_auth(client, db_session):
    lead = _lead(db_session)
    assert _convert(client, lead.id, {"location": LOCATION}).status_code == 401


def test_conversion_is_all_or_nothing(authed_client, db_session, monkeypatch):
    lead = _lead(db_session)

    def explode(*args, **kwargs):
        raise RuntimeError("the property step failed")

    monkeypatch.setattr("app.crud.leads.create_property", explode)
    with pytest.raises(RuntimeError):
        _convert(authed_client, lead.id, {"location": LOCATION})

    # The customer that was created first must not survive the failure
    db_session.expire_all()
    assert db_session.query(Customer).count() == 0
    assert db_session.get(Lead, lead.id).status == LeadStatus.new


def test_converting_twice_creates_nothing_extra(authed_client, db_session):
    lead = _lead(db_session)
    assert _convert(authed_client, lead.id, {"location": LOCATION}).status_code == 201
    assert _convert(authed_client, lead.id, {"location": LOCATION}).status_code == 409
    assert db_session.query(Customer).count() == 1
    assert db_session.query(Property).count() == 1

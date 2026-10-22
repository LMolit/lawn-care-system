import logging

import httpx
import pytest

from app.core.config import settings
from app.services import geocoding

ADDRESS = "100 N Island Ave, Batavia, IL"

# ORS (like most GeoJSON) puts LONGITUDE first
FEATURE = {
    "geometry": {"type": "Point", "coordinates": [-88.3115, 41.8503]},
    "properties": {
        "label": "100 N Island Ave, Batavia, IL, USA",
        "confidence": 1,
        "accuracy": "point",
    },
}


def _response(body, status=200):
    return httpx.Response(
        status, json=body, request=httpx.Request("GET", geocoding.GEOCODE_URL)
    )


class FakeORS:
    """Stands in for the real API. Tests never touch the network."""

    def __init__(self):
        self.calls = []
        self.result = _response({"features": [FEATURE]})

    def get(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


@pytest.fixture()
def ors(monkeypatch):
    fake = FakeORS()
    monkeypatch.setattr("app.services.geocoding.httpx.get", fake.get)
    return fake


def _search(client, q=ADDRESS):
    return client.get("/api/v1/geocode", params={"q": q})


# --- access ---


def test_geocode_requires_auth(client, ors):
    assert _search(client).status_code == 401
    assert ors.calls == []


def test_unauthenticated_requests_cannot_use_up_the_limit(client, ors):
    for _ in range(35):
        assert _search(client).status_code == 401


def test_geocode_is_rate_limited(authed_client, ors):
    for _ in range(30):
        assert _search(authed_client).status_code == 200
    response = _search(authed_client)
    assert response.status_code == 429
    assert response.json()["error"] == "rate_limited"


def test_geocode_needs_a_query(authed_client, ors):
    assert authed_client.get("/api/v1/geocode").status_code == 422


# --- what comes back ---


def test_returns_matches_with_coordinates_the_right_way_round(authed_client, ors):
    response = _search(authed_client)
    assert response.status_code == 200
    assert response.json()["items"] == [
        {
            "label": "100 N Island Ave, Batavia, IL, USA",
            "latitude": 41.8503,
            "longitude": -88.3115,
            "confidence": 1.0,
            "precise": True,
        }
    ]


def test_a_city_level_match_is_marked_not_precise(authed_client, ors):
    centroid = {
        "geometry": {"type": "Point", "coordinates": [-88.31, 41.85]},
        "properties": {
            "label": "Batavia, IL, USA",
            "confidence": 0.4,
            "accuracy": "centroid",
        },
    }
    ors.result = _response({"features": [centroid]})
    assert _search(authed_client).json()["items"][0]["precise"] is False


def test_no_matches_is_an_empty_list_not_an_error(authed_client, ors):
    ors.result = _response({"features": []})
    response = _search(authed_client)
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_malformed_matches_are_skipped(authed_client, ors):
    broken = {"geometry": {"coordinates": ["x", "y"]}, "properties": {}}
    ors.result = _response({"features": [broken, FEATURE]})
    assert len(_search(authed_client).json()["items"]) == 1


def test_impossible_coordinates_are_skipped(authed_client, ors):
    impossible = {
        "geometry": {"coordinates": [-188.0, 95.0]},
        "properties": {"label": "Nowhere"},
    }
    ors.result = _response({"features": [impossible, FEATURE]})
    assert len(_search(authed_client).json()["items"]) == 1


@pytest.mark.parametrize("body", [[], {"features": "nope"}, {"features": None}])
def test_an_unexpected_response_shape_gives_no_results(authed_client, ors, body):
    ors.result = _response(body)
    response = _search(authed_client)
    assert response.status_code == 200
    assert response.json()["items"] == []


# --- what we ask ORS ---


def test_sends_the_right_request(authed_client, ors):
    _search(authed_client)
    call = ors.calls[0]
    assert call["url"] == geocoding.GEOCODE_URL
    assert call["params"]["text"] == ADDRESS
    assert call["params"]["boundary.country"] == "US"
    assert call["params"]["size"] == geocoding.MAX_MATCHES
    assert call["headers"]["Authorization"] == settings.openrouteservice_api_key
    assert call["timeout"]  # never wait forever on a third party


def test_a_query_that_is_too_short_makes_no_request(authed_client, ors):
    response = _search(authed_client, "ab")
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert ors.calls == []


def test_a_blank_query_makes_no_request(authed_client, ors):
    response = _search(authed_client, "     ")
    assert response.json()["items"] == []
    assert ors.calls == []


# --- when ORS misbehaves ---


@pytest.mark.parametrize("status", [401, 429, 500])
def test_provider_errors_become_a_clean_503(authed_client, ors, status):
    ors.result = _response({"detail": "nope"}, status)
    response = _search(authed_client)
    assert response.status_code == 503
    assert response.json()["error"] == "geocoding_unavailable"


def test_a_timeout_becomes_a_clean_503(authed_client, ors):
    ors.result = httpx.ReadTimeout("too slow")
    assert _search(authed_client).status_code == 503


def test_a_non_json_reply_becomes_a_clean_503(authed_client, ors):
    ors.result = httpx.Response(
        200,
        text="<html>gateway</html>",
        request=httpx.Request("GET", geocoding.GEOCODE_URL),
    )
    assert _search(authed_client).status_code == 503


def test_failures_never_leak_the_address_or_key(authed_client, ors, caplog):
    secret_address = "742 Evergreen Terrace, Springfield"
    ors.result = httpx.ReadTimeout("too slow")
    with caplog.at_level(logging.WARNING):
        response = _search(authed_client, secret_address)
    assert secret_address not in response.text
    assert secret_address not in caplog.text
    assert "Geocoding request failed" in caplog.text  # it WAS logged, just safely
    if settings.openrouteservice_api_key:
        assert settings.openrouteservice_api_key not in response.text
        assert settings.openrouteservice_api_key not in caplog.text

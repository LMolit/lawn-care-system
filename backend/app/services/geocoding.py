import logging
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.exceptions import GeocodingUnavailableError

logger = logging.getLogger(__name__)

GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
TIMEOUT_SECONDS = 5.0
MAX_MATCHES = 3


@dataclass(frozen=True)
class GeocodeMatch:
    label: str
    latitude: float
    longitude: float
    confidence: float | None
    precise: bool  # True for a street-address match, False for a city-level guess


def _parse(feature) -> GeocodeMatch | None:
    """Turn one result into a GeocodeMatch, or None if it is unusable."""
    try:
        # GeoJSON coordinates are [longitude, latitude]: the opposite of how people say them
        longitude, latitude = (
            float(value) for value in feature["geometry"]["coordinates"][:2]
        )
        properties = feature.get("properties") or {}
        label = str(properties["label"])
        confidence = properties.get("confidence")
        confidence = float(confidence) if confidence is not None else None
    except (KeyError, TypeError, ValueError, AttributeError):
        return None

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None

    return GeocodeMatch(
        label=label,
        latitude=latitude,
        longitude=longitude,
        confidence=confidence,
        precise=properties.get("accuracy") == "point",
    )


def geocode(address: str) -> list[GeocodeMatch]:
    """Look up an address. Raises GeocodingUnavailableError if the lookup can't be done."""
    try:
        response = httpx.get(
            GEOCODE_URL,
            params={"text": address, "boundary.country": "US", "size": MAX_MATCHES},
            headers={"Authorization": settings.openrouteservice_api_key},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        # Log only the kind of failure. The exception text includes the URL, and the
        # URL includes the address, which is customer data.
        logger.warning("Geocoding request failed: %s", type(exc).__name__)
        raise GeocodingUnavailableError(
            "Address lookup is unavailable right now."
        ) from None

    features = body.get("features") if isinstance(body, dict) else None
    if not isinstance(features, list):
        return []
    return [match for match in (_parse(f) for f in features) if match is not None]

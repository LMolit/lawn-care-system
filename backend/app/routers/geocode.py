from typing import Annotated

from app.schemas.geocode import GeocodeResponse
from fastapi import APIRouter, Depends, Query

from app.core.rate_limit import geocode_limit
from app.dependencies import get_current_user
from app.services import geocoding

router = APIRouter(prefix="/api/v1/geocode", tags=["geocode"])

MIN_QUERY_LENGTH = 3


# The order matters: authentication runs first, so a stranger's requests are
# rejected before they can count against (or use up) the lookup limit.
@router.get(
    "",
    response_model=GeocodeResponse,
    dependencies=[Depends(get_current_user), Depends(geocode_limit)],
)
def search_addresses(q: Annotated[str, Query(max_length=200)]):
    query = q.strip()
    if len(query) < MIN_QUERY_LENGTH:
        # Too short to mean anything: no lookup, no quota spent
        return GeocodeResponse(items=[])
    return GeocodeResponse(items=geocoding.geocode(query))

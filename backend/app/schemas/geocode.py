from pydantic import BaseModel, ConfigDict


class GeocodeMatchResponse(BaseModel):
    label: str
    latitude: float
    longitude: float
    confidence: float | None
    precise: bool

    model_config = ConfigDict(from_attributes=True)


class GeocodeResponse(BaseModel):
    items: list[GeocodeMatchResponse]

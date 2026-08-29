from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class PropertyResponse(BaseModel):
    id: int
    customer_id: int
    address: str
    latitude: float
    longitude: float
    lawn_size_sqft: int | None
    access_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PropertyCreate(BaseModel):
    customer_id: int
    address: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    lawn_size_sqft: int | None = None
    access_notes: str | None = None


class PropertyUpdate(BaseModel):
    customer_id: int | None = None
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    lawn_size_sqft: int | None = None
    access_notes: str | None = None


class PropertyListResponse(BaseModel):
    items: list[PropertyResponse]
    total: int
    page: int
    page_size: int

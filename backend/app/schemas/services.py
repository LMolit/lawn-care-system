# schemas/services.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None
    base_price: float
    estimated_duration_minutes: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    base_price: float
    estimated_duration_minutes: int


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    base_price: float | None = None
    estimated_duration_minutes: int | None = None


class ServiceListResponse(BaseModel):
    items: list[ServiceResponse]
    total: int
    page: int
    page_size: int

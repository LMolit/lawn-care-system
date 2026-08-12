import uuid
from datetime import datetime

from pydantic import BaseModel

from app.db.models.lead import LeadStatus

class LeadCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    address : str
    message: str | None = None

class LeadResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str | None
    phone: str | None
    address: str
    message: str | None
    status: LeadStatus
    converted_customer_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int

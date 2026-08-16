import uuid
from pydantic import BaseModel
from datetime import datetime 

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    notes: str | None
    lead_id : uuid.UUID | None
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomerCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    notes: str | None = None

class CustomerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None
    active: bool | None = None

class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int

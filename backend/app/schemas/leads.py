import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints

from app.db.models.lead import LeadStatus
from app.schemas.types import LongText, ShortText


class LeadCreate(BaseModel):
    name: ShortText
    email: EmailStr | None = None
    phone: Annotated[str, StringConstraints(max_length=30)] | None = None
    address: ShortText
    message: LongText | None = None


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

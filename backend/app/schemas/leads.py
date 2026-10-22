import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints

from app.db.models.lead import LeadStatus
from app.schemas.customers import CustomerResponse
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


class ConvertLocation(BaseModel):
    address: ShortText = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ConvertLeadRequest(BaseModel):
    location: ConvertLocation | None = None


class LeadConversionResponse(CustomerResponse):
    # Everything a customer has, plus the property if one was created
    property_id: int | None = None

# schemas/invoices.py
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.db.base import InvoiceStatus


class InvoiceCreate(BaseModel):
    customer_id: int
    job_ids: list[int]
    due_date: date


class InvoiceLineItemResponse(BaseModel):
    id: int
    job_id: int | None
    description: str
    quantity: float
    unit_price: float
    total: float

    model_config = ConfigDict(from_attributes=True)


class InvoiceResponse(BaseModel):
    id: int
    customer_id: int
    invoice_number: str
    issue_date: date
    due_date: date
    status: InvoiceStatus
    subtotal: float
    tax: float
    total: float
    sent_at: datetime | None
    line_items: list[InvoiceLineItemResponse]

    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int
    page: int
    page_size: int

# schemas/payments.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.base import PaymentMethod


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float
    method: PaymentMethod
    paid_at: datetime
    transaction_ref: str | None = None


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: float
    method: PaymentMethod
    paid_at: datetime
    transaction_ref: str | None

    model_config = ConfigDict(from_attributes=True)

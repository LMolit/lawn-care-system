# routers/payments.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import User
from app.crud import payments as payments_crud
from app.dependencies import get_db, get_current_user
from app.schemas.payments import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("", response_model=PaymentResponse, status_code=201)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return payments_crud.create_payment(
        db,
        invoice_id=payload.invoice_id,
        amount=payload.amount,
        method=payload.method,
        paid_at=payload.paid_at,
        transaction_ref=payload.transaction_ref,
    )

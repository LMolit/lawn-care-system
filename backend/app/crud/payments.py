# crud/payments.py
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.base import Payment, Invoice, InvoiceStatus
from app.exceptions import NotFoundError, ValidationError


def create_payment(db: Session, *, invoice_id: int, amount: float, method, paid_at, transaction_ref: str | None = None) -> Payment:
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise NotFoundError(f"Invoice {invoice_id} not found")

    if invoice.status == InvoiceStatus.draft:
        raise ValidationError(f"Invoice {invoice_id} has not been sent yet")

    payment = Payment(
        invoice_id=invoice_id,
        amount=amount,
        method=method,
        paid_at=paid_at,
        transaction_ref=transaction_ref,
    )
    db.add(payment)
    db.flush()

    total_paid = db.scalar(
        select(func.sum(Payment.amount)).where(Payment.invoice_id == invoice_id)
    )
    if total_paid is not None and total_paid >= invoice.total:
        invoice.status = InvoiceStatus.paid

    db.commit()
    db.refresh(payment)
    return payment

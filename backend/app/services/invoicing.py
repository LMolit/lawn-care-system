from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import InvoiceCounter

def get_next_invoice_number(db: Session) -> str:
    counter = db.execute( select(InvoiceCounter).where(InvoiceCounter.id == 1).with_for_update()).scalar_one()

    counter.count += 1
    db.commit()

    return f"INV-{counter.count:04}"

from sqlalchemy.orm import Session

from app.db.base import Customer

def create_customer(db: Session, *, name: str, email: str | None, phone: str | None,
                    lead_id) -> Customer:
    customer = Customer(name=name, email=email, phone=phone, lead_id=lead_id)
    db.add(customer)
    db.flush()
    return customer

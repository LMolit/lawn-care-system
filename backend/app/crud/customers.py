import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.base import Customer
from app.exceptions import NotFoundError

def create_customer(db: Session, *, name: str, email: str | None, phone: str | None, notes: str |None = None, lead_id: uuid.UUID | None = None) -> Customer:
    customer = Customer(name=name, email=email, phone=phone, notes=notes, lead_id=lead_id)
    db.add(customer)
    db.flush()
    return customer

def get_customer(db: Session, *, id: int) -> Customer:

    return db.get(Customer, id)

def get_customers(db: Session, *, active: bool | None, page: int = 1, page_size: int = 25) -> tuple[list[Customer], int]:
    query = select(Customer)
    count_query = select(func.count()).select_from(Customer)

    if active is not None:
        query = query.where(Customer.active == active)
        count_query = count_query.where(Customer.active == active)

    total = db.scalar(count_query)
    query = query.order_by(Customer.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items =  list(db.scalars(query))

    return items, total


def update_customer(db: Session, *, id: int, name: str | None, email: str | None, phone: str |None, notes: str | None, active: bool | None) -> Customer:

    customer = db.get(Customer, id)

    if customer is None:
        raise NotFoundError(f"Customer {id} not found")

    if name is not None:
        customer.name = name
    if email is not None:
        customer.email = email
    if phone is not None:
        customer.phone = phone
    if notes is not None:
        customer.notes = notes
    if active is not None:
        customer.active = active

    db.commit()
    return customer

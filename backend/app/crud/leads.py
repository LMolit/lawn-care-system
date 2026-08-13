import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.exceptions import NotFoundError, ConflictError
from app.crud.customers import create_customer

from app.db.base import Lead, LeadStatus

def create_lead(db: Session, *, name: str, email: str | None, phone: str | None, address: str, message: str | None) -> Lead:
    lead = Lead(name=name, email=email, phone=phone, address=address, message=message) 
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

def get_lead(db: Session, lead_id: uuid.UUID) -> Lead | None:
    return db.get(Lead, lead_id)

def get_leads(db: Session, *, status: LeadStatus | None = None, page: int = 1, page_size: int =25) -> tuple[list[Lead], int]:
    
    query = select(Lead)
    count_query = select(func.count()).select_from(Lead)

    if status is not None:
        query = query.where(Lead.status == status)
        count_query = count_query.where(Lead.status == status)

    total = db.scalar(count_query)

    query = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(query))

    return items, total

def convert_lead(db: Session, lead_id: uuid.UUID) -> Customer:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise NotFoundError(f"Lead {lead_id} not found")

    if lead.status == LeadStatus.converted:
        raise ConflictError(f"Lead {lead_id} has already been converted")

    customer = create_customer(
        db, name=lead.name, email=lead.email, phone=lead.phone, lead_id=lead.id,
    )

    lead.status = LeadStatus.converted
    lead.converted_customer_id = customer.id

    db.commit()
    db.refresh(customer)
    return customer

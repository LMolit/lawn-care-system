import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.crud.customers import create_customer
from app.crud.properties import create_property
from app.db.base import Customer, Lead, LeadStatus
from app.exceptions import ConflictError, NotFoundError


def create_lead(
    db: Session,
    *,
    name: str,
    email: str | None,
    phone: str | None,
    address: str,
    message: str | None,
) -> Lead:
    lead = Lead(name=name, email=email, phone=phone, address=address, message=message)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: uuid.UUID) -> Lead | None:
    return db.get(Lead, lead_id)


def _escape_like(term: str) -> str:
    # In a LIKE pattern, % and _ are wildcards. Escape them so a search for "%" means "%".
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def get_leads(
    db: Session,
    *,
    status: LeadStatus | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> tuple[list[Lead], int]:

    query = select(Lead)
    count_query = select(func.count()).select_from(Lead)

    if status is not None:
        query = query.where(Lead.status == status)
        count_query = count_query.where(Lead.status == status)

    term = q.strip() if q else ""
    if term:
        pattern = f"%{_escape_like(term)}%"
        matches = or_(
            *(
                column.ilike(pattern, escape="\\")
                for column in (Lead.name, Lead.email, Lead.phone, Lead.address)
            )
        )
        query = query.where(matches)
        count_query = count_query.where(matches)

    total = db.scalar(count_query)

    # id as a tiebreaker keeps pages stable when created_at values match
    query = (
        query.order_by(Lead.created_at.desc(), Lead.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(query))

    return items, total


def count_leads_by_status(db: Session) -> dict[LeadStatus, int]:
    rows = db.execute(select(Lead.status, func.count()).group_by(Lead.status)).all()
    counts = {
        status: 0 for status in LeadStatus
    }  # a status with no rows still shows as 0
    for status, count in rows:
        counts[status] = count
    return counts


def update_lead(db: Session, lead_id: uuid.UUID, changes: dict) -> Lead:
    # Locked like convert_lead, so a status change can't slip in during a conversion.
    lead = db.scalar(
        select(Lead)
        .where(Lead.id == lead_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if lead is None:
        raise NotFoundError(f"Lead {lead_id} not found")

    if changes.get("status") is not None:
        if lead.status == LeadStatus.converted:
            raise ConflictError("A converted lead's status can't be changed")
        lead.status = changes["status"]

    if "notes" in changes:
        lead.notes = changes["notes"] or None  # "" or null clears the note

    db.commit()
    db.refresh(lead)
    return lead


def convert_lead(
    db: Session,
    lead_id: uuid.UUID,
    *,
    property_address: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> tuple[Customer, dict | None]:
    """Turn a lead into a customer, and optionally a property, in ONE transaction."""
    # FOR UPDATE locks the row until we commit, so a double click or two open tabs can't
    # create two customers: the second request waits, then finds the lead already converted.
    # populate_existing makes sure we see the freshly committed status, not a cached copy.
    lead = db.scalar(
        select(Lead)
        .where(Lead.id == lead_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if lead is None:
        raise NotFoundError(f"Lead {lead_id} not found")

    if lead.status == LeadStatus.converted:
        raise ConflictError(f"Lead {lead_id} has already been converted")

    try:
        # commit=False: nothing is saved for good until the single commit below.
        customer = create_customer(
            db,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            lead_id=lead.id,
            commit=False,
        )
        created_property = None
        if property_address is not None:
            created_property = create_property(
                db,
                customer_id=customer.id,
                address=property_address,
                latitude=latitude,
                longitude=longitude,
                commit=False,
            )
        lead.status = LeadStatus.converted
        lead.converted_customer_id = customer.id
        db.commit()
    except Exception:
        db.rollback()  # undo the customer too, so a failure never leaves half a conversion
        raise

    db.refresh(customer)
    return customer, created_property

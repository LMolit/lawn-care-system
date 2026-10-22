import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.core.rate_limit import lead_limit
from app.crud import leads as leads_crud
from app.db.base import LeadStatus
from app.dependencies import get_current_user, get_db
from app.exceptions import NotFoundError
from app.schemas.leads import (
    ConvertLeadRequest,
    LeadAdminResponse,
    LeadConversionResponse,
    LeadCounts,
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadUpdate,
)
from app.services.email import notify_new_lead

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])


@router.post(
    "",
    response_model=LeadResponse,
    status_code=201,
    dependencies=[Depends(lead_limit)],
)
def create_lead(
    payload: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    lead = leads_crud.create_lead(
        db,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        message=payload.message,
    )
    # Runs after the response is sent, so a slow email service never delays the visitor.
    # It gets just the id, not the database object: the session is closed by then.
    background_tasks.add_task(notify_new_lead, lead.id)
    return lead


@router.get(
    "",
    response_model=LeadListResponse,
    dependencies=[Depends(get_current_user)],
)
def list_leads(
    status: LeadStatus | None = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
    db: Session = Depends(get_db),
):
    items, total = leads_crud.get_leads(
        db, status=status, q=q, page=page, page_size=page_size
    )
    return LeadListResponse(items=items, total=total, page=page, page_size=page_size)


# /counts must be declared before /{lead_id}, or "counts" would be read as an id.
@router.get(
    "/counts",
    response_model=LeadCounts,
    dependencies=[Depends(get_current_user)],
)
def count_leads(db: Session = Depends(get_db)):
    counts = leads_crud.count_leads_by_status(db)
    return LeadCounts(**{status.value: n for status, n in counts.items()})


@router.get(
    "/{lead_id}",
    response_model=LeadAdminResponse,
    dependencies=[Depends(get_current_user)],
)
def get_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)):
    lead = leads_crud.get_lead(db, lead_id)
    if lead is None:
        raise NotFoundError(f"Lead {lead_id} not found")
    return lead


@router.patch(
    "/{lead_id}",
    response_model=LeadAdminResponse,
    dependencies=[Depends(get_current_user)],
)
def update_lead(lead_id: uuid.UUID, payload: LeadUpdate, db: Session = Depends(get_db)):
    # exclude_unset: only the fields the client actually sent, so leaving "notes" out
    # leaves the note alone, while sending null or "" clears it.
    return leads_crud.update_lead(db, lead_id, payload.model_dump(exclude_unset=True))


@router.post(
    "/{lead_id}/convert", response_model=LeadConversionResponse, status_code=201
)
def convert_lead(
    lead_id: uuid.UUID,
    payload: ConvertLeadRequest | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    location = payload.location if payload else None
    customer, created_property = leads_crud.convert_lead(
        db,
        lead_id,
        property_address=location.address if location else None,
        latitude=location.latitude if location else None,
        longitude=location.longitude if location else None,
    )
    response = LeadConversionResponse.model_validate(customer)
    response.property_id = created_property["id"] if created_property else None
    return response

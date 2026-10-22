import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.rate_limit import lead_limit
from app.crud import leads as leads_crud
from app.db.base import LeadStatus
from app.dependencies import get_current_user, get_db
from app.schemas.leads import (
    ConvertLeadRequest,
    LeadConversionResponse,
    LeadCreate,
    LeadListResponse,
    LeadResponse,
)

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])


@router.post(
    "",
    response_model=LeadResponse,
    status_code=201,
    dependencies=[Depends(lead_limit)],
)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead = leads_crud.create_lead(
        db,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        message=payload.message,
    )
    return lead


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


@router.get("", response_model=LeadListResponse)
def list_leads(
    status: LeadStatus | None = None,
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items, total = leads_crud.get_leads(
        db, status=status, page=page, page_size=page_size
    )
    return LeadListResponse(items=items, total=total, page=page, page_size=page_size)

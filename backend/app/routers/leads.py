import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import leads as leads_crud
from app.db.base import LeadStatus
from app.dependencies import get_db, get_current_user
from app.schemas.leads import LeadCreate, LeadResponse, LeadListResponse
from app.schemas.customers import CustomerResponse

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])


@router.post("", response_model=LeadResponse, status_code=201)
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

@router.post("/{lead_id}/convert", response_model=CustomerResponse, status_code=201)

def convert_lead(
    lead_id:uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return leads_crud.convert_lead(db, lead_id)


@router.get("", response_model=LeadListResponse)
def list_leads(
    status: LeadStatus | None = None,
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items, total = leads_crud.get_leads(db, status=status, page=page, page_size=page_size)
    return LeadListResponse(items=items, total=total, page=page, page_size=page_size)

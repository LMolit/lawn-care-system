from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import User
from app.crud import invoices as invoices_crud
from app.dependencies import get_db, get_current_user
from app.schemas.invoices import InvoiceCreate, InvoiceResponse

router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceResponse, status_code=201)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return invoices_crud.create_invoice(
        db,
        customer_id=payload.customer_id,
        job_ids=payload.job_ids,
        due_date=payload.due_date,
    )

@router.post("/{id}/send", response_model=InvoiceResponse)
def send_invoice(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return invoices_crud.send_invoice(db, id=id)

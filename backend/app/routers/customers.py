from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import User
from app.crud import customers as customers_crud
from app.dependencies import get_db, get_current_user
from app.schemas.customers import CustomerResponse, CustomerCreate, CustomerUpdate, CustomerListResponse

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])

@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    customer = customers_crud.create_customer(
        db,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        notes=payload.notes,
    )
    return customer

@router.patch("/{id}", response_model=CustomerResponse, status_code=200)
def update_customer(id: int, payload: CustomerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    return customers_crud.update_customer(
        db,
        id=id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        notes=payload.notes,
        active=payload.active,
    )

@router.get("", response_model=CustomerListResponse, status_code=200)
def list_customers(active: bool | None = None, page: int = 1, page_size: int = 25, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    items, total = customers_crud.get_customers(db, active=active, page=page, page_size=page_size)

    return CustomerListResponse(items=items, total=total, page=page, page_size=page_size)




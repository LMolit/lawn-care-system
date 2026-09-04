# routers/services.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import User
from app.crud import services as services_crud
from app.dependencies import get_db, get_current_user
from app.schemas.services import ServiceResponse, ServiceCreate, ServiceUpdate, ServiceListResponse

router = APIRouter(prefix="/api/v1/services", tags=["services"])


@router.post("", response_model=ServiceResponse, status_code=201)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = services_crud.create_service(
        db,
        name=payload.name,
        description=payload.description,
        base_price=payload.base_price,
        estimated_duration_minutes=payload.estimated_duration_minutes,
    )
    return service


@router.patch("/{id}", response_model=ServiceResponse, status_code=200)
def update_service(id: int, payload: ServiceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return services_crud.update_service(
        db,
        id=id,
        name=payload.name,
        description=payload.description,
        base_price=payload.base_price,
        estimated_duration_minutes=payload.estimated_duration_minutes,
    )


@router.get("", response_model=ServiceListResponse, status_code=200)
def list_services(page: int = 1, page_size: int = 25, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items, total = services_crud.get_services(db, page=page, page_size=page_size)
    return ServiceListResponse(items=items, total=total, page=page, page_size=page_size)

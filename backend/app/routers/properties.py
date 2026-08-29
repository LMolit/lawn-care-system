from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.crud import properties as properties_crud
from app.dependencies import get_db, get_current_user
from app.db.base import User
from app.schemas.properties import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyListResponse,
)

router = APIRouter(prefix="/api/v1/properties", tags=["properties"])


@router.post("", response_model=PropertyResponse, status_code=201)
def create_property(
    payload: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return properties_crud.create_property(
        db,
        customer_id=payload.customer_id,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        lawn_size_sqft=payload.lawn_size_sqft,
        access_notes=payload.access_notes,
    )


@router.get("", response_model=PropertyListResponse)
def list_properties(
    customer_id: int | None = None,
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = properties_crud.get_properties(
        db, customer_id=customer_id, page=page, page_size=page_size
    )
    return PropertyListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{id}", response_model=PropertyResponse)
def get_property(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return properties_crud.get_property(db, property_id=id)


@router.patch("/{id}", response_model=PropertyResponse)
def update_property(
    id: int,
    payload: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return properties_crud.update_property(
        db,
        property_id=id,
        customer_id=payload.customer_id,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        lawn_size_sqft=payload.lawn_size_sqft,
        access_notes=payload.access_notes,
    )

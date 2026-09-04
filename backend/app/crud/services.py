# crud/services.py
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.base import Service
from app.exceptions import NotFoundError


def get_service(db: Session, *, id: int) -> Service:
    return db.get(Service, id)


def get_services(db: Session, *, page: int = 1, page_size: int = 25) -> tuple[list[Service], int]:
    query = select(Service)
    count_query = select(func.count()).select_from(Service)

    total = db.scalar(count_query)
    query = query.order_by(Service.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(query))

    return items, total


def create_service(db: Session, *, name: str, description: str | None, base_price: float, estimated_duration_minutes: int) -> Service:
    service = Service(name=name, description=description, base_price=base_price, estimated_duration_minutes=estimated_duration_minutes)
    db.add(service)
    db.commit()
    return service


def update_service(db: Session, *, id: int, name: str | None, description: str | None, base_price: float | None, estimated_duration_minutes: int | None) -> Service:
    service = db.get(Service, id)

    if service is None:
        raise NotFoundError(f"Service {id} not found")

    if name is not None:
        service.name = name
    if description is not None:
        service.description = description
    if base_price is not None:
        service.base_price = base_price
    if estimated_duration_minutes is not None:
        service.estimated_duration_minutes = estimated_duration_minutes

    db.commit()
    return service

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point

from app.db.base import Property
from app.exceptions import NotFoundError


def _property_to_dict(property: Property) -> dict:
    point = to_shape(property.location)
    return {
        "id": property.id,
        "customer_id": property.customer_id,
        "address": property.address,
        "latitude": point.y,
        "longitude": point.x,
        "lawn_size_sqft": property.lawn_size_sqft,
        "access_notes": property.access_notes,
        "created_at": property.created_at,
        "updated_at": property.updated_at,
    }


def get_property(db: Session, *, property_id: int) -> dict:
    property = db.get(Property, property_id)
    if property is None:
        raise NotFoundError(f"Property {property_id} not found")
    return _property_to_dict(property)


def get_properties(db: Session, *, customer_id: int | None = None, page: int = 1, page_size: int = 25) -> tuple[list[dict], int]:
    query = select(Property)
    count_query = select(func.count()).select_from(Property)

    if customer_id is not None:
        query = query.where(Property.customer_id == customer_id)
        count_query = count_query.where(Property.customer_id == customer_id)

    total = db.scalar(count_query)
    query = query.order_by(Property.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(query))

    return [_property_to_dict(p) for p in items], total


def create_property(
    db: Session,
    *,
    customer_id: int,
    address: str,
    latitude: float,
    longitude: float,
    lawn_size_sqft: int | None = None,
    access_notes: str | None = None,
) -> dict:
    location = from_shape(Point(longitude, latitude), srid=4326)
    property = Property(
        customer_id=customer_id,
        address=address,
        location=location,
        lawn_size_sqft=lawn_size_sqft,
        access_notes=access_notes,
    )
    db.add(property)
    db.commit()
    return _property_to_dict(property)


def update_property(
    db: Session,
    *,
    property_id: int,
    customer_id: int | None = None,
    address: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    lawn_size_sqft: int | None = None,
    access_notes: str | None = None,
) -> dict:
    property = db.get(Property, property_id)
    if property is None:
        raise NotFoundError(f"Property {property_id} not found")

    if customer_id is not None:
        property.customer_id = customer_id
    if address is not None:
        property.address = address
    if lawn_size_sqft is not None:
        property.lawn_size_sqft = lawn_size_sqft
    if access_notes is not None:
        property.access_notes = access_notes
    if latitude is not None or longitude is not None:
        current_point = to_shape(property.location)
        new_lat = latitude if latitude is not None else current_point.y
        new_lng = longitude if longitude is not None else current_point.x
        property.location = from_shape(Point(new_lng, new_lat), srid=4326)

    db.commit()
    return _property_to_dict(property)

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import timedelta
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.db.base import Job, Customer, Property, Service, JobEvent, JobStatus, JobEventType
from app.exceptions import NotFoundError, ValidationError, ConflictError


def get_job(db: Session, *, id: int) -> Job:
    job = db.get(Job, id)
    if job is None:
        raise NotFoundError(f"Job {id} not found")
    return job


def get_jobs(db: Session, *, status: str | None = None, customer_id: int | None = None, page: int = 1, page_size: int = 25) -> tuple[list[Job], int]:
    query = select(Job)
    count_query = select(func.count()).select_from(Job)

    if status is not None:
        query = query.where(Job.status == status)
        count_query = count_query.where(Job.status == status)
    if customer_id is not None:
        query = query.where(Job.customer_id == customer_id)
        count_query = count_query.where(Job.customer_id == customer_id)

    total = db.scalar(count_query)
    query = query.order_by(Job.scheduled_date.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(query))

    return items, total


def create_job(
    db: Session,
    *,
    customer_id: int,
    property_id: int,
    service_id: int,
    scheduled_date,
    job_type,
    price: float,
    estimated_duration_minutes: int | None = None,
    notes: str | None = None,
) -> Job:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise NotFoundError(f"Customer {customer_id} not found")

    property = db.get(Property, property_id)
    if property is None:
        raise NotFoundError(f"Property {property_id} not found")
    if property.customer_id != customer_id:
        raise ValidationError(f"Property {property_id} does not belong to customer {customer_id}")

    service = db.get(Service, service_id)
    if service is None:
        raise NotFoundError(f"Service {service_id} not found")

    if estimated_duration_minutes is None:
        estimated_duration_minutes = service.estimated_duration_minutes

    job = Job(
        customer_id=customer_id,
        property_id=property_id,
        service_id=service_id,
        scheduled_date=scheduled_date,
        job_type=job_type,
        price=price,
        estimated_duration_minutes=estimated_duration_minutes,
        notes=notes,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job(
    db: Session,
    *,
    id: int,
    customer_id: int | None = None,
    property_id: int | None = None,
    service_id: int | None = None,
    scheduled_date=None,
    status=None,
    job_type=None,
    price: float | None = None,
    estimated_duration_minutes: int | None = None,
    notes: str | None = None,
) -> Job:
    job = db.get(Job, id)
    if job is None:
        raise NotFoundError(f"Job {id} not found")

    if customer_id is not None:
        job.customer_id = customer_id
    if property_id is not None:
        job.property_id = property_id
    if service_id is not None:
        job.service_id = service_id
    if scheduled_date is not None:
        job.scheduled_date = scheduled_date
    if status is not None:
        job.status = status
    if job_type is not None:
        job.job_type = job_type
    if price is not None:
        job.price = price
    if estimated_duration_minutes is not None:
        job.estimated_duration_minutes = estimated_duration_minutes
    if notes is not None:
        job.notes = notes

    db.commit()
    return job

def start_job(db: Session, *, id: int, latitude: float, longitude: float, timestamp) -> Job:
    job = db.get(Job, id)
    if job is None:
        raise NotFoundError(f"Job {id} not found")

    if job.status != JobStatus.scheduled:
        raise ConflictError(f"Job {id} is not scheduled (current status: {job.status})")

    location = from_shape(Point(longitude, latitude), srid=4326)
    event = JobEvent(
        job_id=id,
        event_type=JobEventType.started,
        timestamp=timestamp,
        location=location,
    )
    db.add(event)

    job.status = JobStatus.in_progress
    db.commit()
    return job


def complete_job(db: Session, *, id: int, latitude: float, longitude: float, timestamp) -> Job:
    job = db.get(Job, id)
    if job is None:
        raise NotFoundError(f"Job {id} not found")

    if job.status != JobStatus.in_progress:
        raise ConflictError(f"Job {id} is not in progress (current status: {job.status})")

    location = from_shape(Point(longitude, latitude), srid=4326)
    event = JobEvent(
        job_id=id,
        event_type=JobEventType.completed,
        timestamp=timestamp,
        location=location,
    )
    db.add(event)

    started_event = db.scalar(
        select(JobEvent)
        .where(JobEvent.job_id == id, JobEvent.event_type == JobEventType.started)
        .order_by(JobEvent.timestamp.desc())
    )
    if started_event is not None:
        elapsed = timestamp - started_event.timestamp
        job.actual_duration_minutes = int(elapsed.total_seconds() / 60)

    job.status = JobStatus.completed
    db.commit()
    return job

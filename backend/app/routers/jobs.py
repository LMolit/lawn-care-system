from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import User
from app.crud import jobs as jobs_crud
from app.dependencies import get_db, get_current_user
from app.schemas.jobs import JobCreate, JobUpdate, JobResponse, JobListResponse

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return jobs_crud.create_job(
        db,
        customer_id=payload.customer_id,
        property_id=payload.property_id,
        service_id=payload.service_id,
        scheduled_date=payload.scheduled_date,
        job_type=payload.job_type,
        price=payload.price,
        estimated_duration_minutes=payload.estimated_duration_minutes,
        notes=payload.notes,
    )


@router.get("", response_model=JobListResponse)
def list_jobs(
    status: str | None = None,
    customer_id: int | None = None,
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = jobs_crud.get_jobs(db, status=status, customer_id=customer_id, page=page, page_size=page_size)
    return JobListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{id}", response_model=JobResponse)
def get_job(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return jobs_crud.get_job(db, id=id)


@router.patch("/{id}", response_model=JobResponse)
def update_job(id: int, payload: JobUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return jobs_crud.update_job(
        db,
        id=id,
        customer_id=payload.customer_id,
        property_id=payload.property_id,
        service_id=payload.service_id,
        scheduled_date=payload.scheduled_date,
        status=payload.status,
        job_type=payload.job_type,
        price=payload.price,
        estimated_duration_minutes=payload.estimated_duration_minutes,
        notes=payload.notes,
    )

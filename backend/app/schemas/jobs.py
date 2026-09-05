from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.db.base import JobStatus, JobType


class JobCreate(BaseModel):
    customer_id: int
    property_id: int
    service_id: int
    scheduled_date: date
    job_type: JobType = JobType.routine
    price: float
    estimated_duration_minutes: int | None = None
    notes: str | None = None

    @field_validator("scheduled_date")
    @classmethod
    def date_not_in_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("scheduled_date cannot be in the past")
        return value


class JobUpdate(BaseModel):
    customer_id: int | None = None
    property_id: int | None = None
    service_id: int | None = None
    scheduled_date: date | None = None
    status: JobStatus | None = None
    job_type: JobType | None = None
    price: float | None = None
    estimated_duration_minutes: int | None = None
    notes: str | None = None

    @field_validator("scheduled_date")
    @classmethod
    def date_not_in_past(cls, value: date | None) -> date | None:
        if value is not None and value < date.today():
            raise ValueError("scheduled_date cannot be in the past")
        return value


class JobResponse(BaseModel):
    id: int
    customer_id: int
    property_id: int
    service_id: int
    scheduled_date: date
    status: JobStatus
    estimated_duration_minutes: int
    actual_duration_minutes: int | None
    price: float
    job_type: JobType
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    page_size: int

class JobEventRequest(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime

import enum
from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin

class JobStatus(str, enum.Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class JobType(str, enum.Enum):
    routine = "routine"
    seasonal = "seasonal"

class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id", ondelete="RESTRICT"), index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    scheduled_date: Mapped[date] = mapped_column(index=True)
    status: Mapped[JobStatus] = mapped_column(default=JobStatus.scheduled)
    estimated_duration_minutes: Mapped[int]
    actual_duration_minutes: Mapped[int | None]
    price: Mapped[float]
    job_type: Mapped[JobType] = mapped_column(default=JobType.routine)
    notes: Mapped[str | None]
    # Note: no reacurrence_id column in phase 1 jobs are created manually

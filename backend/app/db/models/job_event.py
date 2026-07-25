import enum
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

class JobEventType(str, enum.Enum):
    started = "started"
    completed = "completed"

class JobEvent(Base, TimestampMixin):
    __tablename__ = "job_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[JobEventType]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    location: Mapped[str | None] = mapped_column(Geography(geometry_type="POINT", srid=4326))

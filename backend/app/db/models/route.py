import enum
import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RouteStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"


class Route(Base, TimestampMixin):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(index=True)
    status: Mapped[RouteStatus] = mapped_column(default=RouteStatus.planned)
    total_distance_miles: Mapped[float | None]
    total_duration_minutes: Mapped[float | None]
    algorithm_used: Mapped[str] # 


class RouteStop(Base, TimestampMixin):
    __tablename__ = "route_stops"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="RESTRICT"))
    sequence_order: Mapped[int]
    estimated_arrival_time: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    actual_arrival_time: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("route_id", "sequence_order"),)

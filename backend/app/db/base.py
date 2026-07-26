from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class TimestampMixin: 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Import all models here so Base.metadata knows about them
# (Alembic autogenerate only sees tables that have been imported)
from app.db.models.user import User # noqa: F401,E402
from app.db.models.lead import Lead # noqa: F401,E402
from app.db.models.customer import Customer # noqa: F401,E402
from app.db.models.property import Property
from app.db.models.service import Service
from app.db.models.job import Job
from app.db.models.job_event import JobEvent
from app.db.models.route import Route
from app.db.models.review import Review
from app.db.models.invoice import Invoice


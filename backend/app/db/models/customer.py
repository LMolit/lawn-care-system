import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin

class Customer(Base, TimestampMixin):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str | None]
    phone: Mapped[str | None]
    notes: Mapped[str | None]
    lead_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("leads.id"))
    active: Mapped[bool] = mapped_column(default=True)

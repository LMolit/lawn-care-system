import enum
import uuid

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    quoted = "quoted"
    converted = "converted"
    lost = "lost"

class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
        )
    name: Mapped[str]
    email: Mapped[str | None]
    phone: Mapped[str | None]
    address: Mapped[str]
    message: Mapped[str | None]
    status: Mapped[LeadStatus] = mapped_column(default=LeadStatus.new, index=True)
    converted_customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))

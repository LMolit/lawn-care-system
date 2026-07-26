import enum

from datetime import date, datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

class InvoiceStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    paid = "paid"
    overdue = "overdue"
    void = "void"

class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    invoice_number: Mapped[str] = mapped_column(unique=True)
    issue_date: Mapped[date]
    due_date: Mapped[date]
    status: Mapped[InvoiceStatus] = mapped_column(index=True, default=InvoiceStatus.draft)
    subtotal: Mapped[float]
    tax: Mapped[float]
    total: Mapped[float]
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

import enum

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base, TimestampMixin

class PaymentMethod(str, enum.Enum):
    cash = "cash"
    check = "check"
    card = "card"
    online = "online"
    zelle = "zelle"
    venmo = "venmo"

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id", ondelete="RESTRICT"), index=True)
    amount: Mapped[float]
    method: Mapped[PaymentMethod]
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    transaction_ref: Mapped[str | None]

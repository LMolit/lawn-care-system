from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class InvoiceCounter(Base):
      __tablename__ = "invoice_counter"

      id: Mapped[int] = mapped_column(primary_key=True)
      count: Mapped[int] = mapped_column(default=0)

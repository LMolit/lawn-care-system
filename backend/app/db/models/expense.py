
import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime

from app.db.base import Base, TimestampMixin

class ExpenseCategory(Base, TimestampMixin):
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("expense_categories.id"), index=True)
    description: Mapped[str]
    amount: Mapped[float]
    date: Mapped[datetime.date] = mapped_column(index=True)
    vendor: Mapped[str | None]
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"))

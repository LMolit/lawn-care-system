from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str]
    description: Mapped[str | None]
    base_price: Mapped[float]
    estimated_duration_minutes: Mapped[int]

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    customer_id:Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    name: Mapped[str]
    rating: Mapped[int]
    comment: Mapped[str | None]
    approved: Mapped[bool] = mapped_column(default=False, index=True)

    __table_args__ = (CheckConstraint("rating >=1 AND rating <= 5", name="ck_reviews_rating_range"),)

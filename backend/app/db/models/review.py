import enum
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ReviewStatus(str, enum.Enum):
    pending = "pending"  # just submitted, waiting for the owner
    approved = "approved"  # shown on the public site
    hidden = "hidden"  # turned down by the owner: kept, never shown


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    name: Mapped[str]
    rating: Mapped[int]
    comment: Mapped[str | None]
    status: Mapped[ReviewStatus] = mapped_column(
        default=ReviewStatus.pending, index=True
    )

    __table_args__ = (
        CheckConstraint("rating >=1 AND rating <= 5", name="ck_reviews_rating_range"),
    )

    @property
    def approved(self) -> bool:
        # Keeps the public API's `approved` field working, now derived from status.
        return self.status == ReviewStatus.approved

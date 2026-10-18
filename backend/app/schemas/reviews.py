import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.review import ReviewStatus
from app.schemas.types import LongText, ShortText


class ReviewCreate(BaseModel):
    name: ShortText
    rating: int = Field(ge=1, le=5)
    comment: LongText | None = None


# Public: what the website sees. Moderation details stay out of it.
class ReviewResponse(BaseModel):
    id: uuid.UUID
    customer_id: int | None
    name: str
    rating: int
    comment: str | None
    approved: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    page_size: int


# Admin: includes the moderation status.
class ReviewAdminResponse(BaseModel):
    id: uuid.UUID
    customer_id: int | None
    name: str
    rating: int
    comment: str | None
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewAdminListResponse(BaseModel):
    items: list[ReviewAdminResponse]
    total: int
    page: int
    page_size: int


class ReviewCounts(BaseModel):
    pending: int
    approved: int
    hidden: int


class ReviewStatusUpdate(BaseModel):
    status: ReviewStatus

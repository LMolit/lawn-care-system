import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.types import LongText, ShortText


class ReviewCreate(BaseModel):
    name: ShortText
    rating: int = Field(ge=1, le=5)
    comment: LongText | None = None


class ReviewResponse(BaseModel):
    id: uuid.UUID
    customer_id: int | None
    name: str
    rating: int
    comment: str | None
    approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    page_size: int


class ReviewApprove(BaseModel):
    approved: bool

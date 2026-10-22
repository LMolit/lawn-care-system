import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.core.rate_limit import review_limit
from app.crud import reviews as reviews_crud
from app.db.models.review import ReviewStatus
from app.dependencies import get_current_user, get_db
from app.exceptions import NotFoundError
from app.schemas.reviews import (
    ReviewAdminListResponse,
    ReviewAdminResponse,
    ReviewCounts,
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewStatusUpdate,
)
from app.services.email import notify_new_review

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=201,
    dependencies=[Depends(review_limit)],
)
def create_review(
    payload: ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    review = reviews_crud.create_review(
        db,
        name=payload.name,
        rating=payload.rating,
        comment=payload.comment,
    )
    background_tasks.add_task(notify_new_review)
    return review


@router.get("", response_model=ReviewListResponse)
def list_reviews(
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
):
    items, total = reviews_crud.get_approved_reviews(db, page=page, page_size=page_size)
    return ReviewListResponse(items=items, total=total, page=page, page_size=page_size)


# The moderation endpoints. The /admin paths come before /{review_id} on purpose.
@router.get(
    "/admin",
    response_model=ReviewAdminListResponse,
    dependencies=[Depends(get_current_user)],
)
def list_reviews_for_moderation(
    status: ReviewStatus | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
    db: Session = Depends(get_db),
):
    items, total = reviews_crud.get_reviews_for_moderation(
        db, status=status, page=page, page_size=page_size
    )
    return ReviewAdminListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get(
    "/admin/counts",
    response_model=ReviewCounts,
    dependencies=[Depends(get_current_user)],
)
def count_reviews(db: Session = Depends(get_db)):
    counts = reviews_crud.count_reviews_by_status(db)
    return ReviewCounts(**{status.value: n for status, n in counts.items()})


@router.patch(
    "/{review_id}",
    response_model=ReviewAdminResponse,
    dependencies=[Depends(get_current_user)],
)
def update_review_status(
    review_id: uuid.UUID,
    payload: ReviewStatusUpdate,
    db: Session = Depends(get_db),
):
    review = reviews_crud.get_review(db, review_id)
    if review is None:
        raise NotFoundError(f"Review {review_id} not found")
    return reviews_crud.set_review_status(db, review, payload.status)

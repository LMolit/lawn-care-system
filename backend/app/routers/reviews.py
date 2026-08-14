import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import reviews as reviews_crud
from app.dependencies import get_db, get_current_user
from app.exceptions import NotFoundError
from app.schemas.reviews import ReviewCreate, ReviewResponse, ReviewListResponse, ReviewApprove

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=201)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    review = reviews_crud.create_review(
        db,
        name=payload.name,
        rating=payload.rating,
        comment=payload.comment,
    )
    return review


@router.get("", response_model=ReviewListResponse)
def list_reviews(
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
):
    items, total = reviews_crud.get_approved_reviews(db, page=page, page_size=page_size)
    return ReviewListResponse(items=items, total=total, page=page, page_size=page_size)


@router.patch("/{review_id}/approve", response_model=ReviewResponse)
def approve_review(
    review_id: uuid.UUID,
    payload: ReviewApprove,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    review = reviews_crud.get_review(db, review_id)
    if review is None:
        raise NotFoundError(f"Review {review_id} not found")
    return reviews_crud.set_review_approved(db, review, payload.approved)

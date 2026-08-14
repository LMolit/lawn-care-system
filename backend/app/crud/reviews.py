from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Review


def create_review(db: Session, *, name: str, rating: int, comment: str | None) -> Review:
    review = Review(name=name, rating=rating, comment=comment)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_approved_reviews(db: Session, *, page: int = 1, page_size: int = 25) -> tuple[list[Review], int]:
    query = select(Review).where(Review.approved == True)
    count_query = select(func.count()).select_from(Review).where(Review.approved == True)

    total = db.scalar(count_query)

    query = query.order_by(Review.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(query))

    return items, total


def get_review(db: Session, review_id) -> Review | None:
    return db.get(Review, review_id)


def set_review_approved(db: Session, review: Review, approved: bool) -> Review:
    review.approved = approved
    db.commit()
    db.refresh(review)
    return review

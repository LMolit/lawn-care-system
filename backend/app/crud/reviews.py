from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Review
from app.db.models.review import ReviewStatus


def create_review(
    db: Session, *, name: str, rating: int, comment: str | None
) -> Review:
    review = Review(name=name, rating=rating, comment=comment)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_approved_reviews(
    db: Session, *, page: int = 1, page_size: int = 25
) -> tuple[list[Review], int]:
    query = select(Review).where(Review.status == ReviewStatus.approved)
    count_query = (
        select(func.count())
        .select_from(Review)
        .where(Review.status == ReviewStatus.approved)
    )

    total = db.scalar(count_query)

    query = (
        query.order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(query))

    return items, total


def get_reviews_for_moderation(
    db: Session, *, status: ReviewStatus | None, page: int, page_size: int
) -> tuple[list[Review], int]:
    query = select(Review)
    count_query = select(func.count()).select_from(Review)
    if status is not None:
        query = query.where(Review.status == status)
        count_query = count_query.where(Review.status == status)

    total = db.scalar(count_query)

    # id as a tiebreaker keeps pages stable when created_at values match
    query = (
        query.order_by(Review.created_at.desc(), Review.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(db.scalars(query)), total


def count_reviews_by_status(db: Session) -> dict[ReviewStatus, int]:
    rows = db.execute(select(Review.status, func.count()).group_by(Review.status)).all()
    counts = {
        status: 0 for status in ReviewStatus
    }  # a status with no rows still shows as 0
    for status, count in rows:
        counts[status] = count
    return counts


def get_review(db: Session, review_id) -> Review | None:
    return db.get(Review, review_id)


def set_review_status(db: Session, review: Review, status: ReviewStatus) -> Review:
    review.status = status
    db.commit()
    db.refresh(review)
    return review

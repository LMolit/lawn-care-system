from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.base import Expense
from app.exceptions import NotFoundError


def get_expense(db: Session, *, id: int) -> Expense:
    expense = db.get(Expense, id)
    if expense is None:
        raise NotFoundError(f"Expense {id} not found")
    return expense


def get_expenses(db: Session, *, category_id: int | None = None, job_id: int | None = None, page: int = 1, page_size: int = 25) -> tuple[list[Expense], int]:
    query = select(Expense)
    count_query = select(func.count()).select_from(Expense)

    if category_id is not None:
        query = query.where(Expense.category_id == category_id)
        count_query = count_query.where(Expense.category_id == category_id)
    if job_id is not None:
        query = query.where(Expense.job_id == job_id)
        count_query = count_query.where(Expense.job_id == job_id)

    total = db.scalar(count_query)
    query = query.order_by(Expense.date.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(query))

    return items, total


def create_expense(db: Session, *, category_id: int, description: str, amount: float, date, vendor: str | None = None, job_id: int | None = None) -> Expense:
    expense = Expense(category_id=category_id, description=description, amount=amount, date=date, vendor=vendor, job_id=job_id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def update_expense(db: Session, *, id: int, category_id: int | None = None, description: str | None = None, amount: float | None = None, date=None, vendor: str | None = None, job_id: int | None = None) -> Expense:
    expense = db.get(Expense, id)
    if expense is None:
        raise NotFoundError(f"Expense {id} not found")

    if category_id is not None:
        expense.category_id = category_id
    if description is not None:
        expense.description = description
    if amount is not None:
        expense.amount = amount
    if date is not None:
        expense.date = date
    if vendor is not None:
        expense.vendor = vendor
    if job_id is not None:
        expense.job_id = job_id

    db.commit()
    return expense

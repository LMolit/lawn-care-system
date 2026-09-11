from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import User
from app.crud import expenses as expenses_crud
from app.dependencies import get_db, get_current_user
from app.schemas.expenses import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseListResponse

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return expenses_crud.create_expense(
        db,
        category_id=payload.category_id,
        description=payload.description,
        amount=payload.amount,
        date=payload.date,
        vendor=payload.vendor,
        job_id=payload.job_id,
    )


@router.get("", response_model=ExpenseListResponse)
def list_expenses(category_id: int | None = None, job_id: int | None = None, page: int = 1, page_size: int = 25, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items, total = expenses_crud.get_expenses(db, category_id=category_id, job_id=job_id, page=page, page_size=page_size)
    return ExpenseListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{id}", response_model=ExpenseResponse)
def get_expense(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return expenses_crud.get_expense(db, id=id)


@router.patch("/{id}", response_model=ExpenseResponse)
def update_expense(id: int, payload: ExpenseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return expenses_crud.update_expense(
        db,
        id=id,
        category_id=payload.category_id,
        description=payload.description,
        amount=payload.amount,
        date=payload.date,
        vendor=payload.vendor,
        job_id=payload.job_id,
    )

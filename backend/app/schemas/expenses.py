from datetime import date as date_type

from pydantic import BaseModel, ConfigDict


class ExpenseCategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    category_id: int
    description: str
    amount: float
    date: date_type
    vendor: str | None = None
    job_id: int | None = None


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    description: str | None = None
    amount: float | None = None
    date: date_type | None = None
    vendor: str | None = None
    job_id: int | None = None


class ExpenseResponse(BaseModel):
    id: int
    category_id: int
    description: str
    amount: float
    date: date_type
    vendor: str | None
    job_id: int | None

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int

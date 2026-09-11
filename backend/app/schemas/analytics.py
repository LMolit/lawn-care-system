# schemas/analytics.py
from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    revenue_this_month: float
    jobs_completed_this_month: int
    active_customers: int
    avg_job_duration_minutes: float | None


class ExpenseByCategory(BaseModel):
    category: str
    total: float


class ProfitLoss(BaseModel):
    revenue: float
    expenses: float
    profit: float
    expenses_by_category: list[ExpenseByCategory]

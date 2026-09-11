# crud/analytics.py
from datetime import date as date_type

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.base import Invoice, Job, JobStatus, Customer, Expense, ExpenseCategory


def get_overview(db: Session) -> dict:
    today = date_type.today()
    start_of_month = today.replace(day=1)

    revenue_this_month = db.scalar(
        select(func.sum(Invoice.total)).where(
            Invoice.issue_date >= start_of_month, Invoice.issue_date <= today
        )
    ) or 0.0

    jobs_completed_this_month = db.scalar(
        select(func.count()).select_from(Job).where(
            Job.status == JobStatus.completed,
            Job.scheduled_date >= start_of_month,
            Job.scheduled_date <= today,
        )
    ) or 0

    active_customers = db.scalar(
        select(func.count()).select_from(Customer).where(Customer.active == True)
    ) or 0

    avg_job_duration_minutes = db.scalar(
        select(func.avg(Job.actual_duration_minutes)).where(Job.actual_duration_minutes.is_not(None))
    )

    return {
        "revenue_this_month": revenue_this_month,
        "jobs_completed_this_month": jobs_completed_this_month,
        "active_customers": active_customers,
        "avg_job_duration_minutes": avg_job_duration_minutes,
    }


def get_profit_loss(db: Session, *, start_date: date_type, end_date: date_type) -> dict:
    revenue = db.scalar(
        select(func.sum(Invoice.total)).where(
            Invoice.issue_date >= start_date, Invoice.issue_date <= end_date
        )
    ) or 0.0

    expenses = db.scalar(
        select(func.sum(Expense.amount)).where(
            Expense.date >= start_date, Expense.date <= end_date
        )
    ) or 0.0

    profit = revenue - expenses

    rows = db.execute(
        select(ExpenseCategory.name, func.sum(Expense.amount))
        .join(Expense, Expense.category_id == ExpenseCategory.id)
        .where(Expense.date >= start_date, Expense.date <= end_date)
        .group_by(ExpenseCategory.name)
    ).all()

    expenses_by_category = [{"category": name, "total": total} for name, total in rows]

    return {
        "revenue": revenue,
        "expenses": expenses,
        "profit": profit,
        "expenses_by_category": expenses_by_category,
    }

# routers/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.db.base import User
from app.crud import analytics as analytics_crud
from app.dependencies import get_db, get_current_user
from app.schemas.analytics import AnalyticsOverview, ProfitLoss

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return analytics_crud.get_overview(db)


@router.get("/profit-loss", response_model=ProfitLoss)
def get_profit_loss(start_date: date, end_date: date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return analytics_crud.get_profit_loss(db, start_date=start_date, end_date=end_date)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date as date_type

from app.db.base import User
from app.crud import routes as routes_crud
from app.dependencies import get_db, get_current_user
from app.schemas.routes import RouteResponse, RouteGenerateRequest
from app.exceptions import NotFoundError

router = APIRouter(prefix="/api/v1/routes", tags=["routes"])


@router.post("/generate", response_model=RouteResponse, status_code=201)
def generate_route(payload: RouteGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return routes_crud.generate_route(db, route_date=payload.date)


@router.get("/today", response_model=RouteResponse)
def get_todays_route(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    route = routes_crud.get_route_by_date(db, route_date=date_type.today())
    if route is None:
        raise NotFoundError("No route generated for today")
    return route


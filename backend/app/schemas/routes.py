from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.db.base import RouteStatus


class RouteStopResponse(BaseModel):
    id: int
    job_id: int
    sequence_order: int
    estimated_arrival_time: datetime | None
    actual_arrival_time: datetime | None

    model_config = ConfigDict(from_attributes=True)


class RouteResponse(BaseModel):
    id: int
    date: date
    status: RouteStatus
    total_distance_miles: float | None
    total_duration_minutes: float | None
    algorithm_used: str
    stops: list[RouteStopResponse]

    model_config = ConfigDict(from_attributes=True)


class RouteGenerateRequest(BaseModel):
    date: date

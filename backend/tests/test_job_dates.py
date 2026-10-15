from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.jobs import JobCreate, JobUpdate

CHICAGO_EVENING = date(2026, 10, 13)  # 10 PM Oct 13 in Chicago is already Oct 14 in UTC


def _job(scheduled_date):
    return JobCreate(
        customer_id=1,
        property_id=1,
        service_id=1,
        scheduled_date=scheduled_date,
        price=50,
    )


def test_can_schedule_for_local_today_in_the_evening(monkeypatch):
    monkeypatch.setattr("app.schemas.jobs.today_local", lambda: CHICAGO_EVENING)
    assert _job(CHICAGO_EVENING).scheduled_date == CHICAGO_EVENING


def test_cannot_schedule_before_local_today(monkeypatch):
    monkeypatch.setattr("app.schemas.jobs.today_local", lambda: CHICAGO_EVENING)
    with pytest.raises(ValidationError):
        _job(date(2026, 10, 12))


def test_update_can_use_local_today_in_the_evening(monkeypatch):
    monkeypatch.setattr("app.schemas.jobs.today_local", lambda: CHICAGO_EVENING)
    assert JobUpdate(scheduled_date=CHICAGO_EVENING).scheduled_date == CHICAGO_EVENING

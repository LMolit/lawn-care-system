from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.core.config import settings

BUSINESS_TZ = ZoneInfo(settings.business_timezone)


def today_local(now: datetime | None = None) -> date:
    """The current calendar date in the business's timezone.

    `now` must be timezone-aware. It exists so tests can pass a fixed moment.
    """
    current = now or datetime.now(timezone.utc)
    return current.astimezone(BUSINESS_TZ).date()

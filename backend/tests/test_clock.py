from datetime import date, datetime, timezone

from app.core.clock import today_local


def test_summer_evening_is_still_today():
    # 03:30 UTC on Oct 14 is 10:30 PM CDT on Oct 13
    assert today_local(datetime(2026, 10, 14, 3, 30, tzinfo=timezone.utc)) == date(
        2026, 10, 13
    )


def test_winter_evening_is_still_today():
    # 05:30 UTC on Dec 1 is 11:30 PM CST on Nov 30
    assert today_local(datetime(2026, 12, 1, 5, 30, tzinfo=timezone.utc)) == date(
        2026, 11, 30
    )


def test_midday_matches_utc_date():
    assert today_local(datetime(2026, 10, 14, 17, 0, tzinfo=timezone.utc)) == date(
        2026, 10, 14
    )

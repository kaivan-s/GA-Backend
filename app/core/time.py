"""Local-day boundary helpers (brief §5.1: late reset ~3-4am, per-user timezone)."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def now_in(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))


def local_day(tz_name: str, reset_hour: int, at: datetime | None = None) -> date:
    """Return the 'ritual day' for a moment, applying the late-night reset.

    A gratitude entry at 1am with reset_hour=3 still counts for the previous day.
    """
    moment = (at or datetime.now(ZoneInfo(tz_name))).astimezone(ZoneInfo(tz_name))
    shifted = moment - timedelta(hours=reset_hour)
    return shifted.date()


def resolve_beat(tz_name: str, evening_cutoff_hour: int, at: datetime | None = None) -> str:
    """morning before the evening cutoff (local), evening after."""
    moment = (at or datetime.now(ZoneInfo(tz_name))).astimezone(ZoneInfo(tz_name))
    return "morning" if moment.hour < evening_cutoff_hour else "evening"

from __future__ import annotations

from datetime import date

from app.domains.progress.repository import ProgressRepository


class ProgressService:
    def __init__(self, repo: ProgressRepository | None = None):
        self._repo = repo or ProgressRepository()

    def record_beat(self, *, user_id: str, local_day: date, beat: str) -> dict:
        day_stat = self._repo.upsert_day_stat(user_id=user_id, local_day=local_day, beat=beat)
        return {
            "day_stats": self._dot_fields(day_stat),
            "progress": {"days_showed_up": self._repo.days_showed_up(user_id)},
        }

    def summary(self, user_id: str) -> dict:
        return {"days_showed_up": self._repo.days_showed_up(user_id)}

    def calendar(self, user_id: str, start: date, end: date) -> list[dict]:
        from datetime import timedelta
        
        rows = self._repo.calendar(user_id, start, end)
        data_by_day = {r["local_day"]: r for r in rows}
        
        result = []
        current = start
        while current <= end:
            day_str = current.isoformat()
            if day_str in data_by_day:
                result.append({"local_day": day_str, "dot": self._dot(data_by_day[day_str])})
            else:
                result.append({"local_day": day_str, "dot": "none"})
            current += timedelta(days=1)
        
        return result

    @staticmethod
    def _dot(r: dict) -> str:
        if r.get("both_done"):
            return "full"
        if r.get("morning_done") or r.get("evening_done"):
            return "half"
        return "none"

    @staticmethod
    def _dot_fields(r: dict) -> dict:
        return {
            "morning_done": r.get("morning_done", False),
            "evening_done": r.get("evening_done", False),
            "both_done": r.get("both_done", False),
        }

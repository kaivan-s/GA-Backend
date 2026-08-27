from __future__ import annotations

from datetime import date

from app.extensions import get_supabase


class ProgressRepository:
    def upsert_day_stat(self, *, user_id: str, local_day: date, beat: str) -> dict:
        """OR-merge the day rollup so either beat marks the day as 'showed up'.

        Delegates the merge to a Postgres RPC (see migrations) for atomicity.
        """
        get_supabase().client.rpc(
            "upsert_day_stat",
            {
                "p_user_id": user_id,
                "p_local_date": local_day.isoformat(),
                "p_beat": beat,
            },
        ).execute()
        # Return current state
        res = (
            get_supabase()
            .table("day_stats")
            .select("*")
            .eq("user_id", user_id)
            .eq("local_date", local_day.isoformat())
            .limit(1)
            .execute()
        )
        row = (res.data or [{}])[0]
        return {
            "morning_done": row.get("morning", False),
            "evening_done": row.get("evening", False),
            "both_done": row.get("morning", False) and row.get("evening", False),
        }

    def days_showed_up(self, user_id: str) -> int:
        res = (
            get_supabase()
            .table("day_stats")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        return res.count or 0

    def calendar(self, user_id: str, start: date, end: date) -> list[dict]:
        res = (
            get_supabase()
            .table("day_stats")
            .select("local_date, morning, evening")
            .eq("user_id", user_id)
            .gte("local_date", start.isoformat())
            .lte("local_date", end.isoformat())
            .execute()
        )
        return [
            {
                "local_day": r["local_date"],
                "morning_done": r.get("morning", False),
                "evening_done": r.get("evening", False),
                "both_done": r.get("morning", False) and r.get("evening", False),
            }
            for r in (res.data or [])
        ]

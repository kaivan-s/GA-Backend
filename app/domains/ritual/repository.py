from __future__ import annotations

from datetime import date

from app.extensions import get_supabase


class RitualRepository:
    def start_journey(self, user_id: str, journey_id: str) -> dict:
        """Start a journey. Abandons any currently active journey first."""
        # Abandon existing active journeys
        get_supabase().table("user_journeys").update(
            {"status": "abandoned"}
        ).eq("user_id", user_id).eq("status", "active").execute()
        
        # Start new journey
        res = (
            get_supabase()
            .table("user_journeys")
            .insert({"user_id": user_id, "journey_id": journey_id, "status": "active"})
            .execute()
        )
        return res.data[0]

    def active_journey(self, user_id: str) -> dict | None:
        res = (
            get_supabase()
            .table("user_journeys")
            .select("*, journeys(*)")
            .eq("user_id", user_id)
            .eq("status", "active")
            .order("started_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return rows[0] if rows else None

    def journey_day_number(self, user_journey_id: str) -> int:
        res = (
            get_supabase()
            .table("ritual_completions")
            .select("id", count="exact")
            .eq("user_journey_id", user_journey_id)
            .execute()
        )
        return (res.count or 0) + 1

    def completion_exists(
        self, user_id: str, local_date: date, beat: str
    ) -> bool:
        res = (
            get_supabase()
            .table("ritual_completions")
            .select("id")
            .eq("user_id", user_id)
            .eq("local_date", str(local_date))
            .eq("beat", beat)
            .limit(1)
            .execute()
        )
        return bool(res.data)

    def record_completion(
        self,
        user_id: str,
        local_date: date,
        beat: str,
        *,
        prompt_id: str | None,
        user_journey_id: str | None,
    ) -> bool:
        """Record a completion. Returns True if new, False if already existed."""
        try:
            get_supabase().table("ritual_completions").insert(
                {
                    "user_id": user_id,
                    "local_date": str(local_date),
                    "beat": beat,
                    "prompt_id": prompt_id,
                    "user_journey_id": user_journey_id,
                }
            ).execute()
            return True
        except Exception as e:
            # Duplicate key (already completed) - that's fine, idempotent
            if "23505" in str(e) or "duplicate" in str(e).lower():
                return False
            raise

    def save_entry(
        self,
        user_id: str,
        prompt_id: str,
        beat: str,
        local_date: date,
        body: str,
    ) -> dict:
        res = (
            get_supabase()
            .table("journal_entries")
            .insert(
                {
                    "user_id": user_id,
                    "prompt_id": prompt_id,
                    "beat": beat,
                    "local_date": str(local_date),
                    "body": body,
                }
            )
            .execute()
        )
        return res.data[0]

    def complete_journey(self, user_journey_id: str) -> None:
        """Mark a user journey as completed."""
        from datetime import datetime
        get_supabase().table("user_journeys").update(
            {"status": "completed", "completed_at": datetime.utcnow().isoformat()}
        ).eq("id", user_journey_id).execute()

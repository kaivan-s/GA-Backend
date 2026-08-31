from __future__ import annotations

from datetime import datetime

from app.domains.custom_prompts.models import CustomPrompt
from app.extensions import get_supabase

_TABLE = "custom_prompts"


class CustomPromptRepository:
    def list_by_user(self, user_id: str, beat: str | None = None) -> list[CustomPrompt]:
        query = (
            get_supabase()
            .table(_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .eq("is_active", True)
        )
        if beat:
            query = query.eq("beat", beat)
        res = query.order("created_at", desc=True).execute()
        return [self._to_model(r) for r in (res.data or [])]

    def get(self, prompt_id: str) -> CustomPrompt | None:
        res = (
            get_supabase()
            .table(_TABLE)
            .select("*")
            .eq("id", prompt_id)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._to_model(rows[0]) if rows else None

    def create(self, user_id: str, beat: str, body: str) -> CustomPrompt:
        res = (
            get_supabase()
            .table(_TABLE)
            .insert({"user_id": user_id, "beat": beat, "body": body})
            .execute()
        )
        return self._to_model(res.data[0])

    def update(self, prompt_id: str, changes: dict) -> CustomPrompt:
        changes["updated_at"] = datetime.utcnow().isoformat()
        res = (
            get_supabase()
            .table(_TABLE)
            .update(changes)
            .eq("id", prompt_id)
            .execute()
        )
        return self._to_model(res.data[0])

    def delete(self, prompt_id: str) -> None:
        get_supabase().table(_TABLE).update({"is_active": False}).eq("id", prompt_id).execute()

    def count_by_user(self, user_id: str) -> int:
        res = (
            get_supabase()
            .table(_TABLE)
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .execute()
        )
        return res.count or 0

    def get_random(self, user_id: str, beat: str) -> CustomPrompt | None:
        import random
        prompts = self.list_by_user(user_id, beat)
        return random.choice(prompts) if prompts else None

    @staticmethod
    def _to_model(r: dict) -> CustomPrompt:
        return CustomPrompt(
            id=r["id"],
            user_id=r["user_id"],
            beat=r["beat"],
            body=r["body"],
            is_active=r.get("is_active", True),
            created_at=r.get("created_at"),
            updated_at=r.get("updated_at"),
        )

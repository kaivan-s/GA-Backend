from __future__ import annotations

from app.domains.achievements.models import Achievement, UserAchievement
from app.extensions import get_supabase


class AchievementRepository:
    def list_all(self) -> list[Achievement]:
        res = (
            get_supabase()
            .table("achievements")
            .select("*")
            .order("sort_order")
            .execute()
        )
        return [self._to_achievement(r) for r in (res.data or [])]

    def get_by_slug(self, slug: str) -> Achievement | None:
        res = (
            get_supabase()
            .table("achievements")
            .select("*")
            .eq("slug", slug)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._to_achievement(rows[0]) if rows else None

    def list_user_achievements(self, user_id: str) -> list[dict]:
        res = (
            get_supabase()
            .table("user_achievements")
            .select("*, achievements(*)")
            .eq("user_id", user_id)
            .execute()
        )
        return res.data or []

    def has_achievement(self, user_id: str, achievement_id: str) -> bool:
        res = (
            get_supabase()
            .table("user_achievements")
            .select("id")
            .eq("user_id", user_id)
            .eq("achievement_id", achievement_id)
            .limit(1)
            .execute()
        )
        return bool(res.data)

    def award(self, user_id: str, achievement_id: str) -> UserAchievement | None:
        if self.has_achievement(user_id, achievement_id):
            return None
        res = (
            get_supabase()
            .table("user_achievements")
            .insert({"user_id": user_id, "achievement_id": achievement_id})
            .execute()
        )
        return self._to_user_achievement(res.data[0])

    def count_user_achievements(self, user_id: str) -> int:
        res = (
            get_supabase()
            .table("user_achievements")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        return res.count or 0

    @staticmethod
    def _to_achievement(r: dict) -> Achievement:
        return Achievement(
            id=r["id"],
            slug=r["slug"],
            title=r["title"],
            description=r.get("description"),
            icon=r["icon"],
            category=r.get("category", "general"),
            threshold=r.get("threshold"),
            sort_order=r.get("sort_order", 0),
        )

    @staticmethod
    def _to_user_achievement(r: dict) -> UserAchievement:
        return UserAchievement(
            id=r["id"],
            user_id=r["user_id"],
            achievement_id=r["achievement_id"],
            earned_at=r.get("earned_at"),
        )

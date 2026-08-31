from __future__ import annotations

from app.domains.achievements.models import Achievement
from app.domains.achievements.repository import AchievementRepository
from app.extensions import get_supabase


class AchievementService:
    def __init__(self, repo: AchievementRepository | None = None):
        self._repo = repo or AchievementRepository()

    def list_all(self, user_id: str) -> list[dict]:
        all_achievements = self._repo.list_all()
        user_earned = self._repo.list_user_achievements(user_id)
        earned_ids = {ua["achievement_id"] for ua in user_earned}
        earned_times = {ua["achievement_id"]: ua["earned_at"] for ua in user_earned}

        return [
            self._serialize(a, earned=a.id in earned_ids, earned_at=earned_times.get(a.id))
            for a in all_achievements
        ]

    def earned(self, user_id: str) -> list[dict]:
        user_earned = self._repo.list_user_achievements(user_id)
        return [
            {
                "id": ua["achievements"]["id"],
                "slug": ua["achievements"]["slug"],
                "title": ua["achievements"]["title"],
                "description": ua["achievements"].get("description"),
                "icon": ua["achievements"]["icon"],
                "category": ua["achievements"].get("category"),
                "earned_at": ua["earned_at"],
            }
            for ua in user_earned
        ]

    def check_and_award(self, user_id: str) -> list[dict]:
        newly_awarded = []
        stats = self._get_user_stats(user_id)

        for achievement in self._repo.list_all():
            if self._repo.has_achievement(user_id, achievement.id):
                continue
            if self._qualifies(achievement, stats):
                self._repo.award(user_id, achievement.id)
                newly_awarded.append(self._serialize(achievement, earned=True))

        return newly_awarded

    def award_specific(self, user_id: str, slug: str) -> dict | None:
        achievement = self._repo.get_by_slug(slug)
        if not achievement:
            return None
        result = self._repo.award(user_id, achievement.id)
        if result:
            return self._serialize(achievement, earned=True)
        return None

    def _get_user_stats(self, user_id: str) -> dict:
        sb = get_supabase()

        days_res = sb.table("day_stats").select("id", count="exact").eq("user_id", user_id).execute()
        total_days = days_res.count or 0

        entries_res = sb.table("journal_entries").select("id", count="exact").eq("user_id", user_id).execute()
        total_entries = entries_res.count or 0

        journeys_started_res = sb.table("user_journeys").select("id", count="exact").eq("user_id", user_id).execute()
        journeys_started = journeys_started_res.count or 0

        journeys_completed_res = (
            sb.table("user_journeys")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .execute()
        )
        journeys_completed = journeys_completed_res.count or 0

        custom_prompts_res = sb.table("custom_prompts").select("id", count="exact").eq("user_id", user_id).execute()
        custom_prompts = custom_prompts_res.count or 0

        full_days_res = (
            sb.table("day_stats")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("morning", True)
            .eq("evening", True)
            .execute()
        )
        full_days = full_days_res.count or 0

        return {
            "total_days": total_days,
            "total_entries": total_entries,
            "journeys_started": journeys_started,
            "journeys_completed": journeys_completed,
            "custom_prompts": custom_prompts,
            "full_days": full_days,
        }

    def _qualifies(self, a: Achievement, stats: dict) -> bool:
        slug = a.slug
        if slug == "first_day" and stats["total_days"] >= 1:
            return True
        if slug == "week_one" and stats["total_days"] >= 7:
            return True
        if slug == "month_one" and stats["total_days"] >= 30:
            return True
        if slug == "hundred_days" and stats["total_days"] >= 100:
            return True
        if slug == "first_journey" and stats["journeys_started"] >= 1:
            return True
        if slug == "journey_complete" and stats["journeys_completed"] >= 1:
            return True
        if slug == "first_entry" and stats["total_entries"] >= 1:
            return True
        if slug == "ten_entries" and stats["total_entries"] >= 10:
            return True
        if slug == "both_beats" and stats["full_days"] >= 1:
            return True
        if slug == "custom_created" and stats["custom_prompts"] >= 1:
            return True
        return False

    @staticmethod
    def _serialize(a: Achievement, earned: bool, earned_at: str | None = None) -> dict:
        return {
            "id": a.id,
            "slug": a.slug,
            "title": a.title,
            "description": a.description,
            "icon": a.icon,
            "category": a.category,
            "earned": earned,
            "earned_at": earned_at,
        }

from __future__ import annotations

from app.config import get_settings
from app.core.auth.entitlement import has_premium
from app.core.time import local_day, resolve_beat
from app.domains.content.repository import ContentRepository
from app.domains.content.service import ContentService
from app.domains.progress.service import ProgressService
from app.domains.ritual.repository import RitualRepository
from app.domains.users.models import User
from app.errors import NotFound


class RitualService:
    def __init__(
        self,
        repo: RitualRepository | None = None,
        content: ContentService | None = None,
        content_repo: ContentRepository | None = None,
        progress: ProgressService | None = None,
    ):
        self._repo = repo or RitualRepository()
        self._content = content or ContentService()
        self._content_repo = content_repo or ContentRepository()
        self._progress = progress or ProgressService()

    def today(self, user: User, tz: str) -> dict:
        settings = get_settings()
        beat = resolve_beat(tz, settings.evening_cutoff_hour)
        day = local_day(tz, user.day_reset_hour)
        entitled = has_premium(user.id)

        # Check if already completed this beat today
        already_completed = self._repo.completion_exists(user.id, day, beat)

        journey_row = self._repo.active_journey(user.id)
        prompt = None
        journey_payload = None
        if journey_row:
            current_day = self._repo.journey_day_number(journey_row["id"])
            prompt = self._content_repo.prompt_for_journey_day(
                journey_row["journey_id"], current_day, beat
            )
            journey_payload = {
                "current_day": current_day,
            }

        if prompt is None:
            prompt = self._content_repo.pick_default_prompt(beat, free_only=not entitled)

        # Never leave the user on a blank page (brief §4.2): fall back to free content.
        if prompt is None or (prompt.is_premium and not entitled):
            prompt = self._content_repo.pick_default_prompt(beat, free_only=True)
        if prompt is None:
            raise NotFound("No content available for this beat.")

        return {
            "beat": beat,
            "completed": already_completed,
            "prompt": {
                "id": prompt.id,
                "beat": prompt.beat,
                "body": prompt.body,
                "audio_url": self._content.audio_url(prompt),
            },
            "journey": journey_payload,
            "progress": self._progress.summary(user.id),
            "entitlement": {"tier": "premium" if entitled else "free"},
        }

    def complete(self, user: User, prompt_id: str, beat: str, tz: str) -> dict:
        from app.domains.achievements.service import AchievementService

        day = local_day(tz, user.day_reset_hour)
        journey_row = self._repo.active_journey(user.id)
        is_new = self._repo.record_completion(
            user_id=user.id, local_date=day, beat=beat,
            prompt_id=prompt_id, user_journey_id=journey_row["id"] if journey_row else None,
        )
        
        journey_completed = None
        if is_new:
            result = self._progress.record_beat(user_id=user.id, local_day=day, beat=beat)
            newly_awarded = AchievementService().check_and_award(user.id)
            result["newly_awarded"] = newly_awarded
            
            # Check for journey completion (evening beat of last day)
            if journey_row and beat == "evening":
                journey_completed = self._check_journey_completion(user.id, journey_row)
                if journey_completed:
                    result["newly_awarded"] = AchievementService().check_and_award(user.id)
        else:
            result = {
                "day_stats": {"morning_done": beat == "morning", "evening_done": beat == "evening", "both_done": False},
                "progress": self._progress.summary(user.id),
                "newly_awarded": [],
            }
        
        response = {"recorded": True, "already_done": not is_new, "local_day": day.isoformat(), **result}
        if journey_completed:
            response["journey_completed"] = journey_completed
        return response
    
    def _check_journey_completion(self, user_id: str, journey_row: dict) -> dict | None:
        """Check if the user just completed their journey, and if so mark it complete."""
        current_day = self._repo.journey_day_number(journey_row["id"])
        journey = self._content_repo.get_journey_by_id(journey_row["journey_id"])
        
        if not journey or current_day < journey.length_days:
            return None
        
        # User has reached the last day - mark journey as completed
        self._repo.complete_journey(journey_row["id"])
        
        return {
            "title": journey.title,
            "length_days": journey.length_days,
            "is_premium": journey.is_premium,
        }

    def save_entry(self, user: User, prompt_id: str, beat: str, body: str, tz: str) -> dict:
        from app.domains.achievements.service import AchievementService

        day = local_day(tz, user.day_reset_hour)
        self._repo.save_entry(
            user_id=user.id, prompt_id=prompt_id, beat=beat,
            local_date=day, body=body,
        )
        newly_awarded = AchievementService().check_and_award(user.id)
        return {"saved": True, "local_day": day.isoformat(), "newly_awarded": newly_awarded}

    def start_journey(self, user: User, journey_id: str) -> dict:
        """Start a journey for the user. Entitlement check should be done by caller."""
        from app.domains.achievements.service import AchievementService

        journey = self._content_repo.get_journey_by_id(journey_id)
        if not journey:
            raise NotFound("Journey not found.")
        self._repo.start_journey(user.id, journey_id)
        AchievementService().award_specific(user.id, "first_journey")
        return {
            "started": True,
            "journey": {
                "id": journey.id,
                "title": journey.title,
                "length_days": journey.length_days,
            },
        }

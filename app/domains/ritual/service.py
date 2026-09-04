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
from app.extensions import get_supabase


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
        from app.domains.programs.service import ProgramsService
        from app.domains.values.repository import ValuesRepository
        
        settings = get_settings()
        beat = resolve_beat(tz, settings.evening_cutoff_hour)
        day = local_day(tz, user.day_reset_hour)
        entitled = has_premium(user.id)

        # Check if already completed this beat today
        already_completed = self._repo.completion_exists(user.id, day, beat)

        # Check for active program first (takes precedence over journeys)
        program_state = ProgramsService().get_active_program_state(user.id)
        program_payload = None
        prompt_payload = None
        journey_payload = None
        morning_loop = None
        
        if program_state and program_state.get("day"):
            # User has an active program - source content from it
            prog_day = program_state["day"]
            program_payload = {
                "id": program_state["program"]["id"],
                "slug": program_state["program"]["slug"],
                "title": program_state["program"]["title"],
                "current_day": program_state["current_day"],
                "duration_days": program_state["program"]["duration_days"],
                "phase": program_state.get("phase"),
                "is_final_day": program_state.get("is_final_day", False),
            }
            
            if beat == "morning":
                prompt_payload = {
                    "id": f"program-{program_state['program']['id']}-day{program_state['current_day']}-morning",
                    "beat": "morning",
                    "body": prog_day["morning_question"],  # The question is the main prompt
                    "context": prog_day["morning_prompt"],  # The framing context
                    "micro_teaching": prog_day.get("micro_teaching"),
                    "content_type": "question",  # Program prompts are reflective questions → "Reflect" action
                }
            else:
                prompt_payload = {
                    "id": f"program-{program_state['program']['id']}-day{program_state['current_day']}-evening",
                    "beat": "evening",
                    "body": prog_day["evening_question"],  # The question is the main prompt
                    "context": prog_day["evening_prompt"],  # The framing context
                    "causation_prompt": "What made this possible?",  # Always include for evening
                    "micro_teaching": prog_day.get("micro_teaching"),
                    "content_type": "question",  # Program prompts are reflective questions → "Reflect" action
                }

        if prompt_payload is None:
            # Fall back to journey or default prompts
            from app.domains.morning.service import MorningService
            
            journey_row = self._repo.active_journey(user.id)
            prompt = None
            journey_payload = None
            morning_loop = None
            
            if journey_row:
                current_day = self._repo.journey_day_number(journey_row["id"])
                prompt = self._content_repo.prompt_for_journey_day(
                    journey_row["journey_id"], current_day, beat
                )
                journey_payload = {"current_day": current_day}

            if prompt is None:
                if beat == "morning":
                    # Use Morning Loop for morning beat (reflects user's own entries)
                    morning_msg = MorningService().get_morning_message(user.id)
                    morning_loop = {
                        "source_type": morning_msg.source_type,
                        "context": morning_msg.context,
                    }
                    prompt_payload = {
                        "id": f"morning-{morning_msg.source_type}-{morning_msg.source_id or 'generic'}",
                        "beat": "morning",
                        "body": morning_msg.body,
                        "go_deeper_question": morning_msg.go_deeper_question,
                        "content_type": morning_msg.content_type,  # "received" or "question" for action label
                    }
                else:
                    prompt = self._content_repo.pick_default_prompt(beat, free_only=not entitled)

            if prompt is not None:
                if prompt.is_premium and not entitled:
                    prompt = self._content_repo.pick_default_prompt(beat, free_only=True)
                if prompt is None:
                    raise NotFound("No content available for this beat.")

                prompt_payload = {
                    "id": prompt.id,
                    "beat": prompt.beat,
                    "body": prompt.body,
                    "audio_url": self._content.audio_url(prompt),
                    "content_type": "question",  # Journey/default prompts are reflective questions
                }
                if prompt.causation_prompt:
                    prompt_payload["causation_prompt"] = prompt.causation_prompt
                if prompt.value_id:
                    value = self._get_value_info(prompt.value_id)
                    if value:
                        prompt_payload["value"] = value

        response = {
            "beat": beat,
            "completed": already_completed,
            "prompt": prompt_payload,
            "progress": self._progress.summary(user.id),
            "entitlement": {"tier": "premium" if entitled else "free"},
        }
        
        if program_payload:
            response["program"] = program_payload
        elif journey_payload:
            response["journey"] = journey_payload
        
        # Include morning loop info if present
        if morning_loop:
            response["morning_loop"] = morning_loop
        
        return response
    
    def _get_value_info(self, value_id: str) -> dict | None:
        """Get value name and icon for display."""
        res = (
            get_supabase()
            .table("values")
            .select("name, icon")
            .eq("id", value_id)
            .limit(1)
            .execute()
        )
        if res.data:
            return {"name": res.data[0]["name"], "icon": res.data[0].get("icon")}
        return None

    def complete(self, user: User, prompt_id: str, beat: str, tz: str) -> dict:
        from app.domains.achievements.service import AchievementService
        from app.domains.programs.service import ProgramsService

        day = local_day(tz, user.day_reset_hour)
        journey_row = self._repo.active_journey(user.id)
        
        # For synthetic prompts (program/morning-loop), we don't have a real prompt_id in the database
        # These are generated dynamically and not stored in the prompts table
        is_synthetic = prompt_id.startswith("program-") or prompt_id.startswith("morning-")
        actual_prompt_id = None if is_synthetic else prompt_id
        
        is_new = self._repo.record_completion(
            user_id=user.id, local_date=day, beat=beat,
            prompt_id=actual_prompt_id, user_journey_id=journey_row["id"] if journey_row else None,
        )
        
        journey_completed = None
        program_completed = None
        program_day_advanced = None
        
        if is_new:
            result = self._progress.record_beat(user_id=user.id, local_day=day, beat=beat)
            newly_awarded = AchievementService().check_and_award(user.id)
            result["newly_awarded"] = newly_awarded
            
            # Check for program day advancement (both beats completed)
            if result["day_stats"]["both_done"]:
                program_result = ProgramsService().advance_program_day(user.id)
                if program_result:
                    if program_result.get("completed"):
                        program_completed = program_result
                        newly_awarded = AchievementService().check_and_award(user.id)
                        result["newly_awarded"] = newly_awarded
                    else:
                        program_day_advanced = program_result
            
            # Check for journey completion (evening beat of last day)
            if journey_row and beat == "evening" and not program_completed:
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
        if program_completed:
            response["program_completed"] = program_completed
        if program_day_advanced:
            response["program_day_advanced"] = program_day_advanced
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

    def save_entry(
        self, user: User, prompt_id: str, beat: str, body: str, tz: str,
        causation_text: str | None = None,
    ) -> dict:
        from app.domains.achievements.service import AchievementService
        from app.domains.morning.service import MorningService

        day = local_day(tz, user.day_reset_hour)
        
        # For synthetic prompts (program/morning-loop), we don't have a real prompt_id in the database
        is_synthetic = prompt_id.startswith("program-") or prompt_id.startswith("morning-")
        actual_prompt_id = None if is_synthetic else prompt_id
        
        entry_row = self._repo.save_entry(
            user_id=user.id, prompt_id=actual_prompt_id, beat=beat,
            local_date=day, body=body, causation_text=causation_text,
        )
        
        # Mark evening entries as loop-safe (gratitude is positive by construction)
        # Evening entries feed the next morning's loop
        entry_id = entry_row.get("id") if entry_row else None
        if beat == "evening" and entry_id and body and len(body.strip()) > 10:
            MorningService().mark_entry_for_loop(entry_id, is_positive=True)
        
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

from __future__ import annotations

from app.core.auth.entitlement import has_premium
from app.domains.programs.models import Program, ProgramDay, ProgramPhase, UserProgram
from app.domains.programs.repository import ProgramsRepository
from app.errors import Forbidden, NotFound


class ProgramsService:
    def __init__(self, repo: ProgramsRepository | None = None):
        self._repo = repo or ProgramsRepository()

    def list_programs(self, user_id: str) -> list[dict]:
        """List all programs with access state for the user."""
        programs = self._repo.list_programs()
        entitled = has_premium(user_id)
        active_up = self._repo.get_active_user_program(user_id)
        
        result = []
        for p in programs:
            locked = p.access == "premium" and not entitled
            is_active = active_up and active_up.program_id == p.id
            
            result.append({
                "id": p.id,
                "slug": p.slug,
                "title": p.title,
                "subtitle": p.subtitle,
                "theme": p.theme,
                "duration_days": p.duration_days,
                "access": p.access,
                "locked": locked,
                "is_active": is_active,
                "has_disclaimer": bool(p.disclaimer_copy),
            })
        
        return result

    def get_program_detail(self, user_id: str, program_id: str) -> dict:
        """Get detailed program info for the detail/start screen."""
        program = self._repo.get_program(program_id)
        if not program:
            raise NotFound("Program not found.")
        
        entitled = has_premium(user_id)
        locked = program.access == "premium" and not entitled
        
        phases = self._repo.get_phases(program_id)
        active_up = self._repo.get_active_user_program(user_id)
        
        # Get day 1 sample for preview
        day1 = self._repo.get_day(program_id, 1)
        
        # Check if user has completed this program before
        history = self._repo.get_user_program_history(user_id)
        completed_before = any(
            up.program_id == program_id and up.status == "completed"
            for up in history
        )
        
        return {
            "id": program.id,
            "slug": program.slug,
            "title": program.title,
            "subtitle": program.subtitle,
            "theme": program.theme,
            "duration_days": program.duration_days,
            "access": program.access,
            "is_rerunnable": program.is_rerunnable,
            "intro_copy": program.intro_copy,
            "disclaimer_copy": program.disclaimer_copy,
            "completion_copy": program.completion_copy,
            "locked": locked,
            "phases": [
                {
                    "phase_number": ph.phase_number,
                    "title": ph.title,
                    "teaching_copy": ph.teaching_copy,
                    "start_day": ph.start_day,
                    "end_day": ph.end_day,
                }
                for ph in phases
            ],
            "sample_day": {
                "morning_prompt": day1.morning_prompt,
                "morning_question": day1.morning_question,
                "evening_prompt": day1.evening_prompt,
                "evening_question": day1.evening_question,
            } if day1 else None,
            "has_active_program": active_up is not None,
            "is_this_active": active_up and active_up.program_id == program.id,
            "current_day": active_up.current_day if active_up and active_up.program_id == program.id else None,
            "completed_before": completed_before,
        }

    def start_program(self, user_id: str, program_id: str) -> dict:
        """Start a program. Abandons any active program first."""
        program = self._repo.get_program(program_id)
        if not program:
            raise NotFound("Program not found.")
        
        # Check entitlement for premium programs
        if program.access == "premium" and not has_premium(user_id):
            raise Forbidden("Premium subscription required for this program.")
        
        # Abandon any active program
        self._repo.abandon_active_program(user_id)
        
        # Start new program
        user_program = self._repo.start_program(user_id, program_id)
        
        return {
            "started": True,
            "program": {
                "id": program.id,
                "title": program.title,
                "duration_days": program.duration_days,
            },
            "current_day": 1,
            "run_count": user_program.run_count,
        }

    def get_active_program_state(self, user_id: str) -> dict | None:
        """Get the user's active program state for the Today screen."""
        user_program = self._repo.get_active_user_program(user_id)
        if not user_program:
            return None
        
        program = self._repo.get_program(user_program.program_id)
        if not program:
            return None
        
        phase = self._repo.get_phase_for_day(program.id, user_program.current_day)
        day = self._repo.get_day(program.id, user_program.current_day)
        
        # Check if this is the first day of a new phase (for teaching display)
        is_phase_start = phase and phase.start_day == user_program.current_day
        
        return {
            "user_program_id": user_program.id,
            "program": {
                "id": program.id,
                "slug": program.slug,
                "title": program.title,
                "duration_days": program.duration_days,
            },
            "current_day": user_program.current_day,
            "phase": {
                "number": phase.phase_number if phase else None,
                "title": phase.title if phase else None,
                "teaching_copy": phase.teaching_copy if is_phase_start else None,
            } if phase else None,
            "day": {
                "morning_prompt": day.morning_prompt if day else None,
                "morning_question": day.morning_question if day else None,
                "evening_prompt": day.evening_prompt if day else None,
                "evening_question": day.evening_question if day else None,
                "micro_teaching": day.micro_teaching if day else None,
            } if day else None,
            "is_final_day": user_program.current_day >= program.duration_days,
        }

    def advance_program_day(self, user_id: str) -> dict | None:
        """Called after completing both beats of a program day."""
        user_program = self._repo.get_active_user_program(user_id)
        if not user_program:
            return None
        
        program = self._repo.get_program(user_program.program_id)
        if not program:
            return None
        
        if user_program.current_day >= program.duration_days:
            # Program complete
            self._repo.complete_program(user_program.id)
            return {
                "completed": True,
                "program": {
                    "id": program.id,
                    "title": program.title,
                },
                "completion_copy": program.completion_copy,
            }
        else:
            # Advance to next day
            new_day = user_program.current_day + 1
            self._repo.advance_day(user_program.id, new_day)
            return {
                "completed": False,
                "new_day": new_day,
            }

    def abandon_program(self, user_id: str) -> dict:
        """Explicitly abandon the active program."""
        user_program = self._repo.get_active_user_program(user_id)
        if not user_program:
            return {"abandoned": False, "message": "No active program"}
        
        self._repo.abandon_active_program(user_id)
        return {"abandoned": True}

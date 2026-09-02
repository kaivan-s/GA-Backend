from __future__ import annotations

from datetime import datetime

from app.domains.programs.models import Program, ProgramDay, ProgramPhase, UserProgram
from app.extensions import get_supabase


class ProgramsRepository:
    def list_programs(self) -> list[Program]:
        """List all active programs."""
        res = (
            get_supabase()
            .table("programs")
            .select("*")
            .eq("is_active", True)
            .order("sort_order")
            .execute()
        )
        return [self._program(r) for r in (res.data or [])]

    def get_program(self, program_id: str) -> Program | None:
        res = (
            get_supabase()
            .table("programs")
            .select("*")
            .eq("id", program_id)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._program(rows[0]) if rows else None

    def get_program_by_slug(self, slug: str) -> Program | None:
        res = (
            get_supabase()
            .table("programs")
            .select("*")
            .eq("slug", slug)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._program(rows[0]) if rows else None

    def get_phases(self, program_id: str) -> list[ProgramPhase]:
        res = (
            get_supabase()
            .table("program_phases")
            .select("*")
            .eq("program_id", program_id)
            .order("phase_number")
            .execute()
        )
        return [self._phase(r) for r in (res.data or [])]

    def get_phase_for_day(self, program_id: str, day_number: int) -> ProgramPhase | None:
        """Get the phase that contains a specific day."""
        res = (
            get_supabase()
            .table("program_phases")
            .select("*")
            .eq("program_id", program_id)
            .lte("start_day", day_number)
            .gte("end_day", day_number)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._phase(rows[0]) if rows else None

    def get_day(self, program_id: str, day_number: int) -> ProgramDay | None:
        res = (
            get_supabase()
            .table("program_days")
            .select("*")
            .eq("program_id", program_id)
            .eq("day_number", day_number)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._day(rows[0]) if rows else None

    def get_active_user_program(self, user_id: str) -> UserProgram | None:
        """Get user's currently active program enrollment."""
        res = (
            get_supabase()
            .table("user_programs")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .order("started_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._user_program(rows[0]) if rows else None

    def get_user_program_history(self, user_id: str) -> list[UserProgram]:
        """Get all user's program enrollments."""
        res = (
            get_supabase()
            .table("user_programs")
            .select("*")
            .eq("user_id", user_id)
            .order("started_at", desc=True)
            .execute()
        )
        return [self._user_program(r) for r in (res.data or [])]

    def start_program(self, user_id: str, program_id: str) -> UserProgram:
        """Start a new program enrollment."""
        # Check if user has run this program before
        existing = (
            get_supabase()
            .table("user_programs")
            .select("id, run_count")
            .eq("user_id", user_id)
            .eq("program_id", program_id)
            .order("run_count", desc=True)
            .limit(1)
            .execute()
        ).data
        
        run_count = 1
        if existing:
            run_count = existing[0]["run_count"] + 1

        res = (
            get_supabase()
            .table("user_programs")
            .insert({
                "user_id": user_id,
                "program_id": program_id,
                "current_day": 1,
                "status": "active",
                "run_count": run_count,
            })
            .execute()
        )
        return self._user_program(res.data[0])

    def abandon_active_program(self, user_id: str) -> None:
        """Abandon user's currently active program."""
        get_supabase().table("user_programs").update({
            "status": "abandoned",
            "last_activity_at": datetime.utcnow().isoformat(),
        }).eq("user_id", user_id).eq("status", "active").execute()

    def advance_day(self, user_program_id: str, new_day: int) -> None:
        """Advance program to next day."""
        get_supabase().table("user_programs").update({
            "current_day": new_day,
            "last_activity_at": datetime.utcnow().isoformat(),
        }).eq("id", user_program_id).execute()

    def complete_program(self, user_program_id: str) -> None:
        """Mark program as completed."""
        get_supabase().table("user_programs").update({
            "status": "completed",
            "last_activity_at": datetime.utcnow().isoformat(),
        }).eq("id", user_program_id).execute()

    def update_activity(self, user_program_id: str) -> None:
        """Update last activity timestamp."""
        get_supabase().table("user_programs").update({
            "last_activity_at": datetime.utcnow().isoformat(),
        }).eq("id", user_program_id).execute()

    @staticmethod
    def _program(r: dict) -> Program:
        return Program(
            id=r["id"],
            slug=r["slug"],
            title=r["title"],
            subtitle=r.get("subtitle"),
            theme=r.get("theme"),
            duration_days=r.get("duration_days", 14),
            access=r.get("access", "premium"),
            is_rerunnable=r.get("is_rerunnable", True),
            intro_copy=r.get("intro_copy"),
            disclaimer_copy=r.get("disclaimer_copy"),
            completion_copy=r.get("completion_copy"),
            sort_order=r.get("sort_order", 0),
            is_active=r.get("is_active", True),
        )

    @staticmethod
    def _phase(r: dict) -> ProgramPhase:
        return ProgramPhase(
            id=r["id"],
            program_id=r["program_id"],
            phase_number=r["phase_number"],
            title=r["title"],
            teaching_copy=r.get("teaching_copy"),
            start_day=r["start_day"],
            end_day=r["end_day"],
        )

    @staticmethod
    def _day(r: dict) -> ProgramDay:
        return ProgramDay(
            id=r["id"],
            program_id=r["program_id"],
            day_number=r["day_number"],
            phase_number=r["phase_number"],
            morning_prompt=r["morning_prompt"],
            morning_question=r["morning_question"],
            evening_prompt=r["evening_prompt"],
            evening_question=r["evening_question"],
            micro_teaching=r.get("micro_teaching"),
        )

    @staticmethod
    def _user_program(r: dict) -> UserProgram:
        return UserProgram(
            id=r["id"],
            user_id=r["user_id"],
            program_id=r["program_id"],
            current_day=r["current_day"],
            started_at=r.get("started_at"),
            last_activity_at=r.get("last_activity_at"),
            status=r["status"],
            run_count=r.get("run_count", 1),
        )

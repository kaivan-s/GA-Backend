from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Program:
    id: str
    slug: str
    title: str
    subtitle: str | None
    theme: str | None
    duration_days: int
    access: str  # "free" | "premium"
    is_rerunnable: bool
    intro_copy: str | None
    disclaimer_copy: str | None
    completion_copy: str | None
    sort_order: int
    is_active: bool


@dataclass
class ProgramPhase:
    id: str
    program_id: str
    phase_number: int  # 1, 2, or 3
    title: str
    teaching_copy: str | None
    start_day: int
    end_day: int


@dataclass
class ProgramDay:
    id: str
    program_id: str
    day_number: int
    phase_number: int
    morning_prompt: str
    morning_question: str
    evening_prompt: str
    evening_question: str
    micro_teaching: str | None


@dataclass
class UserProgram:
    id: str
    user_id: str
    program_id: str
    current_day: int
    started_at: datetime | None
    last_activity_at: datetime | None
    status: str  # "active" | "completed" | "abandoned"
    run_count: int

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Theme:
    id: str
    slug: str
    title: str
    palette: str
    is_premium: bool
    sort_order: int


@dataclass
class Prompt:
    id: str
    theme_id: str | None
    beat: str  # "morning" | "evening"
    body: str
    audio_path: str | None
    is_free: bool
    is_premium: bool
    is_active: bool
    causation_prompt: str | None = None  # "Why did this happen?" follow-up
    angle: str | None = None  # For evening prompt rotation


@dataclass
class Journey:
    id: str
    slug: str
    theme_id: str | None
    title: str
    description: str | None
    length_days: int
    is_free: bool
    is_premium: bool
    cover_path: str | None
    is_active: bool

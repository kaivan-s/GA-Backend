from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Achievement:
    id: str
    slug: str
    title: str
    description: str | None
    icon: str
    category: str
    threshold: int | None
    sort_order: int = 0


@dataclass
class UserAchievement:
    id: str
    user_id: str
    achievement_id: str
    earned_at: datetime | None = None

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class User:
    id: str
    clerk_user_id: str
    email: str | None
    display_name: str | None
    timezone: str
    day_reset_hour: int

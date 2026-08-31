from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CustomPrompt:
    id: str
    user_id: str
    beat: str
    body: str
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

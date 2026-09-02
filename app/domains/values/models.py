from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Value:
    id: str
    slug: str
    name: str
    description: str | None
    icon: str | None
    sort_order: int
    is_active: bool

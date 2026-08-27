"""Simple offset pagination helpers."""
from __future__ import annotations

from dataclasses import dataclass

from flask import request


@dataclass
class Page:
    limit: int
    offset: int

    @classmethod
    def from_request(cls, *, default_limit: int = 20, max_limit: int = 100) -> Page:
        try:
            limit = min(int(request.args.get("limit", default_limit)), max_limit)
            offset = max(int(request.args.get("offset", 0)), 0)
        except ValueError:
            limit, offset = default_limit, 0
        return cls(limit=limit, offset=offset)

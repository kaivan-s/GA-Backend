from __future__ import annotations

from app.domains.content.models import Journey, Theme


def serialize_theme(t: Theme) -> dict:
    return {
        "slug": t.slug,
        "title": t.title,
        "palette": t.palette,
        "is_premium": t.is_premium,
    }


def serialize_journey(j: Journey, *, entitled: bool) -> dict:
    return {
        "id": j.id,
        "slug": j.slug,
        "title": j.title,
        "description": j.description,
        "length_days": j.length_days,
        "is_free": j.is_free,
        "is_premium": j.is_premium,
        "locked": j.is_premium and not entitled,
    }

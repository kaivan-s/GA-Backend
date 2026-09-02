from __future__ import annotations

from pydantic import BaseModel, Field

from app.domains.values.models import Value


class SetValuesRequest(BaseModel):
    value_ids: list[str] = Field(min_length=1, max_length=10)


def serialize_value(v: Value, *, selected: bool = False) -> dict:
    return {
        "id": v.id,
        "slug": v.slug,
        "name": v.name,
        "description": v.description,
        "icon": v.icon,
        "selected": selected,
    }

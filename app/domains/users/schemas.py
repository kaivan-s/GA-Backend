from __future__ import annotations

from pydantic import BaseModel, Field

from app.domains.users.models import User


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=80)
    timezone: str | None = None
    day_reset_hour: int | None = Field(default=None, ge=0, le=6)


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "timezone": user.timezone,
        "day_reset_hour": user.day_reset_hour,
    }

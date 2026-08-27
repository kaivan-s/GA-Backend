from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterDeviceRequest(BaseModel):
    apns_token: str
    platform: str = "ios"
    morning_reminder: bool = True
    evening_reminder: bool = True
    morning_time: str | None = Field(default="08:00")
    evening_time: str | None = Field(default="21:00")

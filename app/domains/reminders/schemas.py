from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterDeviceRequest(BaseModel):
    device_token: str
    platform: str = "ios"
    morning_time: str = Field(default="08:00")
    evening_time: str = Field(default="20:00")
    is_active: bool = True

from __future__ import annotations

from pydantic import BaseModel, field_validator


class CreateCustomPromptRequest(BaseModel):
    beat: str
    body: str

    @field_validator("beat")
    @classmethod
    def validate_beat(cls, v: str) -> str:
        if v not in ("morning", "evening"):
            raise ValueError("beat must be 'morning' or 'evening'")
        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("body cannot be empty")
        if len(v) > 500:
            raise ValueError("body must be 500 characters or less")
        return v


class UpdateCustomPromptRequest(BaseModel):
    body: str

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("body cannot be empty")
        if len(v) > 500:
            raise ValueError("body must be 500 characters or less")
        return v

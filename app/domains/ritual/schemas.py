from __future__ import annotations

from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    prompt_id: str
    beat: str = Field(pattern="^(morning|evening)$")


class EntryRequest(BaseModel):
    prompt_id: str
    beat: str = Field(pattern="^(morning|evening)$")
    body: str = Field(min_length=1, max_length=5000)

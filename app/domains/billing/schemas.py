from __future__ import annotations

from pydantic import BaseModel


class AppleVerifyRequest(BaseModel):
    signed_transaction: str

from __future__ import annotations

from pydantic import BaseModel


class VerifyTransactionRequest(BaseModel):
    signed_transaction: str

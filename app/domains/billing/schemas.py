from __future__ import annotations

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    product_id: str

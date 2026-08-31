from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# Map Dodo Payments product IDs to tier
PRODUCT_TIER: dict[str, str] = {
    "pdt_0NmZs3H0pUIeAQZ9W1Lhv": "premium",  # Monthly
    "pdt_0NmZsFERjXg9vp4rwg1oM": "premium",  # Yearly
}


@dataclass
class Entitlement:
    user_id: str
    tier: str  # 'free' | 'premium'
    product_id: str | None = None
    source: str = "dodo"  # 'dodo' | 'apple' | 'promo' | 'gift'
    original_transaction_id: str | None = None
    expires_at: datetime | None = None
    is_trial: bool = False
    status: str = "active"  # 'active' | 'expired' | 'cancelled' | 'revoked'

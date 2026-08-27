from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

PRODUCT_TIER: dict[str, str] = {
    "com.gratidude.premium.monthly": "premium",
    "com.gratidude.premium.yearly": "premium",
}


@dataclass
class Entitlement:
    user_id: str
    tier: str  # 'free' | 'premium'
    product_id: str | None = None
    source: str = "apple"  # 'apple' | 'promo' | 'gift'
    original_transaction_id: str | None = None
    expires_at: datetime | None = None
    is_trial: bool = False
    status: str = "active"  # 'active' | 'expired' | 'grace_period' | 'revoked'

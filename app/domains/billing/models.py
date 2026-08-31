from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# Map Dodo Payments product IDs to tier
# Update these with your actual Dodo product IDs from the dashboard
PRODUCT_TIER: dict[str, str] = {
    # Dodo Payments product IDs (replace with actual IDs)
    "pdt_gratidude_monthly": "premium",
    "pdt_gratidude_yearly": "premium",
    # Legacy Apple IDs (if still needed)
    "com.gratidude.premium.monthly": "premium",
    "com.gratidude.premium.yearly": "premium",
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

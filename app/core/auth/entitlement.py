"""@require_premium: gate premium *content* only. Core ritual is never blocked (brief §6)."""
from __future__ import annotations

from datetime import UTC, datetime
from functools import wraps

from app.core.auth.middleware import current_user
from app.errors import UpgradeRequired


def has_premium(user_id: str) -> bool:
    from app.domains.billing.service import BillingService

    ent = BillingService().get_entitlement(user_id)
    if not ent or ent.tier != "premium":
        return False
    return ent.expires_at is None or ent.expires_at > datetime.now(UTC)


def require_premium(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not has_premium(user.id):
            raise UpgradeRequired("This content is part of Premium.")
        return fn(*args, **kwargs)

    return wrapper

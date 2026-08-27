from __future__ import annotations

from datetime import datetime

from app.domains.billing.models import Entitlement
from app.extensions import get_supabase

_TABLE = "entitlements"


class BillingRepository:
    def get(self, user_id: str) -> Entitlement | None:
        res = (
            get_supabase().table(_TABLE).select("*").eq("user_id", user_id).limit(1).execute()
        )
        rows = res.data or []
        return self._to_model(rows[0]) if rows else None

    def upsert(self, entitlement: Entitlement) -> Entitlement:
        payload = {
            "user_id": entitlement.user_id,
            "tier": entitlement.tier,
            "product_id": entitlement.product_id,
            "source": entitlement.source,
            "original_transaction_id": entitlement.original_transaction_id,
            "expires_at": entitlement.expires_at.isoformat() if entitlement.expires_at else None,
            "is_trial": entitlement.is_trial,
            "status": entitlement.status,
        }
        res = get_supabase().table(_TABLE).upsert(payload, on_conflict="user_id").execute()
        return self._to_model(res.data[0])

    @staticmethod
    def _to_model(r: dict) -> Entitlement:
        expires = r.get("expires_at")
        return Entitlement(
            user_id=r["user_id"],
            tier=r.get("tier", "free"),
            product_id=r.get("product_id"),
            source=r.get("source", "apple"),
            original_transaction_id=r.get("original_transaction_id"),
            expires_at=datetime.fromisoformat(expires) if expires else None,
            is_trial=r.get("is_trial", False),
            status=r.get("status", "active"),
        )

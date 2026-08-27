from __future__ import annotations

from datetime import UTC, datetime

from app.domains.billing.apple import AppleClient
from app.domains.billing.models import PRODUCT_TIER, Entitlement
from app.domains.billing.repository import BillingRepository


class BillingService:
    def __init__(self, repo: BillingRepository | None = None, apple: AppleClient | None = None):
        self._repo = repo or BillingRepository()
        self._apple = apple or AppleClient()

    def get_entitlement(self, user_id: str) -> Entitlement | None:
        return self._repo.get(user_id)

    def entitlement_summary(self, user_id: str) -> dict:
        ent = self._repo.get(user_id)
        if not ent:
            return {"tier": "free"}
        active = ent.tier == "premium" and (
            ent.expires_at is None or ent.expires_at > datetime.now(UTC)
        )
        return {
            "tier": "premium" if active else "free",
            "product_id": ent.product_id,
            "expires_at": ent.expires_at.isoformat() if ent.expires_at else None,
            "is_trial": ent.is_trial,
            "status": ent.status,
        }

    def verify_apple_transaction(self, user_id: str, signed_jws: str) -> dict:
        tx = self._apple.verify_signed_transaction(signed_jws)
        tier = PRODUCT_TIER.get(tx.product_id, "free")
        ent = Entitlement(
            user_id=user_id,
            tier=tier,
            product_id=tx.product_id,
            source="apple",
            original_transaction_id=tx.original_transaction_id,
            expires_at=tx.expires_at,
            is_trial=tx.is_trial,
            status="active",
        )
        self._repo.upsert(ent)
        return self.entitlement_summary(user_id)

    def apply_notification(self, signed_payload: str) -> None:
        """Handle ASSN v2 (renew/expire/refund). Idempotent by notificationUUID (TODO store)."""
        data = self._apple.decode_notification(signed_payload)
        # Full mapping of notificationType -> entitlement status change lives here.
        _ = data  # placeholder until renewal-info decoding is wired

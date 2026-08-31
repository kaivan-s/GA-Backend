from __future__ import annotations

import os
from datetime import UTC, datetime

from app.domains.billing.dodo import DodoClient
from app.domains.billing.models import PRODUCT_TIER, Entitlement
from app.domains.billing.repository import BillingRepository
from app.domains.users.repository import UserRepository


class BillingService:
    def __init__(
        self,
        repo: BillingRepository | None = None,
        dodo: DodoClient | None = None,
        users_repo: UserRepository | None = None,
    ):
        self._repo = repo or BillingRepository()
        self._dodo = dodo or DodoClient()
        self._users = users_repo or UserRepository()

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

    def create_checkout(self, user_id: str, product_id: str) -> dict:
        """Create a Dodo Payments checkout session for subscription."""
        user = self._users.get_by_id(user_id)
        
        base_url = os.environ.get("APP_BASE_URL", "https://gratitude-app-backend.guild-space.co")
        return_url = f"{base_url}/v1/billing/success?user_id={user_id}"
        
        session = self._dodo.create_checkout_session(
            product_id=product_id,
            customer_email=user.email if user else None,
            return_url=return_url,
            metadata={"user_id": user_id},
        )
        
        return {
            "checkout_url": session.checkout_url,
            "session_id": session.session_id,
        }

    def handle_dodo_webhook(self, raw_body: str, headers: dict) -> None:
        """Handle Dodo Payments webhook events."""
        event = self._dodo.verify_webhook(raw_body, headers)
        
        if event.event_type == "subscription.active":
            self._activate_subscription(event)
        elif event.event_type == "subscription.renewed":
            self._renew_subscription(event)
        elif event.event_type == "subscription.cancelled":
            self._cancel_subscription(event)
        elif event.event_type == "subscription.expired":
            self._expire_subscription(event)

    def _activate_subscription(self, event) -> None:
        """Activate a new subscription."""
        user_id = self._get_user_id_from_event(event)
        if not user_id:
            return
        
        tier = PRODUCT_TIER.get(event.product_id, "premium")
        ent = Entitlement(
            user_id=user_id,
            tier=tier,
            product_id=event.product_id,
            source="dodo",
            original_transaction_id=event.subscription_id,
            expires_at=None,
            is_trial=False,
            status="active",
        )
        self._repo.upsert(ent)

    def _renew_subscription(self, event) -> None:
        """Handle subscription renewal."""
        user_id = self._get_user_id_from_event(event)
        if not user_id:
            return
        
        ent = self._repo.get(user_id)
        if ent:
            ent.status = "active"
            self._repo.upsert(ent)

    def _cancel_subscription(self, event) -> None:
        """Handle subscription cancellation."""
        user_id = self._get_user_id_from_event(event)
        if not user_id:
            return
        
        ent = self._repo.get(user_id)
        if ent:
            ent.status = "cancelled"
            self._repo.upsert(ent)

    def _expire_subscription(self, event) -> None:
        """Handle subscription expiration."""
        user_id = self._get_user_id_from_event(event)
        if not user_id:
            return
        
        ent = self._repo.get(user_id)
        if ent:
            ent.tier = "free"
            ent.status = "expired"
            self._repo.upsert(ent)

    def _get_user_id_from_event(self, event) -> str | None:
        """Extract user_id from webhook event metadata or customer lookup."""
        metadata = event.payload.get("data", {}).get("metadata", {})
        return metadata.get("user_id")

    def cancel_subscription(self, user_id: str) -> dict:
        """Cancel the user's active subscription."""
        ent = self._repo.get(user_id)
        if not ent or not ent.original_transaction_id:
            return {"cancelled": False, "message": "No active subscription found."}
        
        try:
            self._dodo.cancel_subscription(ent.original_transaction_id)
            ent.status = "cancelled"
            self._repo.upsert(ent)
            return {"cancelled": True, "message": "Subscription cancelled successfully."}
        except Exception as e:
            return {"cancelled": False, "message": str(e)}

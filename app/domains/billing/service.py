from __future__ import annotations

from datetime import UTC, datetime

from app.domains.billing.apple import AppleClient, get_apple_client
from app.domains.billing.models import PRODUCT_TIER, Entitlement
from app.domains.billing.repository import BillingRepository
from app.domains.users.repository import UserRepository


class BillingService:
    def __init__(
        self,
        repo: BillingRepository | None = None,
        apple: AppleClient | None = None,
        users_repo: UserRepository | None = None,
    ):
        self._repo = repo or BillingRepository()
        self._apple = apple or get_apple_client()
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

    def verify_apple_transaction(self, user_id: str, signed_transaction: str) -> dict:
        """Verify a StoreKit 2 signed transaction and grant entitlement.
        
        Called by iOS app after successful purchase to sync entitlement with backend.
        """
        try:
            tx = self._apple.verify_signed_transaction(signed_transaction)
            
            tier = PRODUCT_TIER.get(tx.product_id, "premium")
            ent = Entitlement(
                user_id=user_id,
                tier=tier,
                product_id=tx.product_id,
                source="apple",
                original_transaction_id=tx.original_transaction_id,
                expires_at=tx.expires_at,
                is_trial=tx.is_trial,
                status="active" if tx.is_active else "expired",
            )
            self._repo.upsert(ent)
            
            return {
                "verified": True,
                "tier": tier,
                "product_id": tx.product_id,
                "expires_at": tx.expires_at.isoformat() if tx.expires_at else None,
                "is_trial": tx.is_trial,
            }
        except Exception as e:
            print(f"[BillingService] Transaction verification failed: {e}")
            return {"verified": False, "error": str(e)}

    def handle_apple_notification(self, signed_payload: str) -> None:
        """Handle App Store Server Notification v2.
        
        Updates entitlement status based on subscription lifecycle events.
        """
        try:
            notification = self._apple.decode_notification(signed_payload)
            print(f"[Apple Webhook] {notification.notification_type} / {notification.subtype}")
            
            if not notification.original_transaction_id:
                print("[Apple Webhook] No transaction ID in notification")
                return
            
            # Find entitlement by original_transaction_id
            ent = self._repo.get_by_transaction_id(notification.original_transaction_id)
            if not ent:
                print(f"[Apple Webhook] No entitlement found for transaction {notification.original_transaction_id}")
                return
            
            # Update based on notification type
            if notification.notification_type in ("SUBSCRIBED", "DID_RENEW", "OFFER_REDEEMED"):
                ent.status = "active"
                ent.tier = "premium"
                if notification.transaction:
                    ent.expires_at = notification.transaction.expires_at
                    ent.is_trial = notification.transaction.is_trial
                    
            elif notification.notification_type == "EXPIRED":
                ent.status = "expired"
                ent.tier = "free"
                
            elif notification.notification_type == "DID_FAIL_TO_RENEW":
                ent.status = "grace_period" if notification.subtype == "GRACE_PERIOD" else "billing_retry"
                
            elif notification.notification_type in ("REFUND", "REVOKE"):
                ent.status = "revoked"
                ent.tier = "free"
                
            elif notification.notification_type == "DID_CHANGE_RENEWAL_STATUS":
                if notification.subtype == "AUTO_RENEW_DISABLED":
                    ent.status = "will_expire"
                elif notification.subtype == "AUTO_RENEW_ENABLED":
                    ent.status = "active"
            
            self._repo.upsert(ent)
            print(f"[Apple Webhook] Updated entitlement for user {ent.user_id}: {ent.status}")
            
        except Exception as e:
            print(f"[Apple Webhook] Error processing notification: {e}")

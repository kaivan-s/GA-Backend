from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.billing.service import BillingService

bp = Blueprint("billing", __name__)


@bp.get("/v1/entitlement")
@require_auth
def get_entitlement():
    """Get the current user's entitlement status."""
    user = current_user()
    return jsonify(BillingService().entitlement_summary(user.id))


@bp.post("/v1/billing/verify")
@require_auth
def verify_transaction():
    """Verify a StoreKit 2 signed transaction and grant entitlement.
    
    iOS app sends the signed transaction JWS after a successful purchase.
    Backend verifies and records the entitlement.
    """
    user = current_user()
    data = request.get_json(silent=True) or {}
    signed_transaction = data.get("signed_transaction", "")
    
    if not signed_transaction:
        return jsonify({"error": "signed_transaction required"}), 400
    
    result = BillingService().verify_apple_transaction(user.id, signed_transaction)
    return jsonify(result)


@bp.post("/webhooks/apple")
def apple_webhook():
    """Handle App Store Server Notifications v2.
    
    Apple sends these for subscription lifecycle events:
    - SUBSCRIBED: New subscription started
    - DID_RENEW: Subscription renewed
    - EXPIRED: Subscription expired
    - REFUND: User was refunded
    - DID_FAIL_TO_RENEW: Billing issue
    """
    data = request.get_json(silent=True) or {}
    signed_payload = data.get("signedPayload", "")
    
    if not signed_payload:
        return jsonify({"error": "signedPayload required"}), 400
    
    BillingService().handle_apple_notification(signed_payload)
    return jsonify({"received": True})

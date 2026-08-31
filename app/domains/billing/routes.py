from __future__ import annotations

from flask import Blueprint, jsonify, redirect, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.billing.schemas import CheckoutRequest
from app.domains.billing.service import BillingService

bp = Blueprint("billing", __name__)


@bp.get("/v1/entitlement")
@require_auth
def get_entitlement():
    user = current_user()
    return jsonify(BillingService().entitlement_summary(user.id))


@bp.post("/v1/billing/checkout")
@require_auth
def create_checkout():
    """Create a Dodo Payments checkout session for subscription."""
    user = current_user()
    payload = CheckoutRequest(**(request.get_json(silent=True) or {}))
    result = BillingService().create_checkout(user.id, payload.product_id)
    return jsonify(result)


@bp.get("/v1/billing/success")
def checkout_success():
    """Redirect page after successful checkout. iOS app should handle this deep link."""
    return jsonify({"status": "success", "message": "Payment completed! Return to the app."})


@bp.post("/v1/billing/cancel")
@require_auth
def cancel_subscription():
    """Cancel the user's active subscription."""
    user = current_user()
    result = BillingService().cancel_subscription(user.id)
    return jsonify(result)


@bp.post("/webhooks/dodo")
def dodo_webhook():
    """Handle Dodo Payments webhook events."""
    raw_body = request.get_data(as_text=True)
    headers = {
        "webhook-id": request.headers.get("webhook-id", ""),
        "webhook-signature": request.headers.get("webhook-signature", ""),
        "webhook-timestamp": request.headers.get("webhook-timestamp", ""),
    }
    BillingService().handle_dodo_webhook(raw_body, headers)
    return jsonify({"received": True})

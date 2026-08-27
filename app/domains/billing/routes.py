from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.billing.schemas import AppleVerifyRequest
from app.domains.billing.service import BillingService

bp = Blueprint("billing", __name__)


@bp.get("/v1/entitlement")
@require_auth
def get_entitlement():
    user = current_user()
    return jsonify(BillingService().entitlement_summary(user.id))


@bp.post("/v1/billing/apple/verify")
@require_auth
def verify_apple():
    user = current_user()
    payload = AppleVerifyRequest(**(request.get_json(silent=True) or {}))
    summary = BillingService().verify_apple_transaction(user.id, payload.signed_transaction)
    return jsonify(summary)


@bp.post("/webhooks/apple")
def apple_webhook():
    body = request.get_json(silent=True) or {}
    signed = body.get("signedPayload", "")
    BillingService().apply_notification(signed)
    return jsonify({"received": True})

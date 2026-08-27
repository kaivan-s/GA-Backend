"""Clerk webhook: keep the app user table in sync with Clerk identity events."""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from svix.webhooks import Webhook, WebhookVerificationError

from app.config import get_settings
from app.domains.users.service import UserService
from app.errors import Unauthenticated

bp = Blueprint("user_webhooks", __name__)


def _primary_email(data: dict) -> str | None:
    emails = data.get("email_addresses") or []
    if not emails:
        return None
    primary_id = data.get("primary_email_address_id")
    for e in emails:
        if e.get("id") == primary_id:
            return e.get("email_address")
    return emails[0].get("email_address")


@bp.post("/webhooks/clerk")
def clerk_webhook():
    secret = get_settings().clerk_webhook_secret
    try:
        payload = Webhook(secret).verify(request.get_data(), dict(request.headers))
    except WebhookVerificationError as exc:
        raise Unauthenticated("Invalid webhook signature.") from exc

    event_type = payload.get("type")
    data = payload.get("data", {})
    service = UserService()

    if event_type in ("user.created", "user.updated"):
        service.sync_from_webhook(clerk_user_id=data["id"], email=_primary_email(data))

    return jsonify({"received": True})

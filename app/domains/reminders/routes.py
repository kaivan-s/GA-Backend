from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.reminders.apns import ApnsClient
from app.domains.reminders.schemas import RegisterDeviceRequest
from app.domains.reminders.service import ReminderService
from app.extensions import get_supabase

bp = Blueprint("reminders", __name__)


@bp.post("/v1/reminders/device")
@require_auth
def register_device():
    user = current_user()
    payload = RegisterDeviceRequest(**(request.get_json(silent=True) or {}))
    device = ReminderService().register(user.id, payload.model_dump())
    return jsonify({"device": device}), 201


@bp.delete("/v1/reminders/device/<device_token>")
@require_auth
def delete_device(device_token: str):
    user = current_user()
    ReminderService().remove_by_token(user.id, device_token)
    return jsonify({"deleted": True})


@bp.post("/v1/reminders/test")
@require_auth
def test_notification():
    """Send a test notification to the current user's devices."""
    user = current_user()
    
    res = get_supabase().table("devices").select("device_token").eq("user_id", user.id).eq("is_active", True).execute()
    tokens = [d["device_token"] for d in (res.data or [])]
    
    if not tokens:
        return jsonify({"error": "No devices registered"}), 400
    
    apns = ApnsClient()
    results = apns.send_batch(tokens, "Test Notification", "Push notifications are working!")
    
    sent = sum(1 for v in results.values() if v)
    return jsonify({
        "sent": sent,
        "total": len(tokens),
        "message": f"Sent {sent}/{len(tokens)} test notifications"
    })

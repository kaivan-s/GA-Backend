from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.reminders.schemas import RegisterDeviceRequest
from app.domains.reminders.service import ReminderService

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

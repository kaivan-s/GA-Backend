from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.reminders.schemas import RegisterDeviceRequest
from app.domains.reminders.service import ReminderService

bp = Blueprint("reminders", __name__)


@bp.post("/v1/devices")
@require_auth
def register_device():
    user = current_user()
    payload = RegisterDeviceRequest(**(request.get_json(silent=True) or {}))
    device = ReminderService().register(user.id, payload.model_dump())
    return jsonify({"device": device}), 201


@bp.delete("/v1/devices/<device_id>")
@require_auth
def delete_device(device_id: str):
    user = current_user()
    ReminderService().remove(user.id, device_id)
    return jsonify({"deleted": True})

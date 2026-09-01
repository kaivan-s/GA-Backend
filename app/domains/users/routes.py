from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.billing.service import BillingService
from app.domains.users.schemas import UpdateProfileRequest, serialize_user
from app.domains.users.service import UserService

bp = Blueprint("users", __name__)


@bp.get("/v1/me")
@require_auth
def get_me():
    user = current_user()
    ent = BillingService().entitlement_summary(user.id)
    return jsonify({"user": serialize_user(user), "entitlement": ent})


@bp.patch("/v1/me")
@require_auth
def update_me():
    user = current_user()
    payload = UpdateProfileRequest(**(request.get_json(silent=True) or {}))
    updated = UserService().update_profile(user.id, payload.model_dump())
    return jsonify({"user": serialize_user(updated)})


@bp.delete("/v1/me")
@require_auth
def delete_me():
    """
    Permanently delete the current user's account and all associated data.
    Required by Apple App Store Guidelines for apps with account creation.
    """
    user = current_user()
    result = UserService().delete_account(user)
    return jsonify(result)

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.values.repository import ValuesRepository
from app.domains.values.schemas import SetValuesRequest, serialize_value

bp = Blueprint("values", __name__)


@bp.get("/v1/values")
@require_auth
def list_values():
    """List all available values with user's selections marked."""
    user = current_user()
    repo = ValuesRepository()
    
    all_values = repo.list_all()
    user_value_ids = set(repo.get_user_value_ids(user.id))
    
    return jsonify({
        "values": [
            serialize_value(v, selected=(v.id in user_value_ids))
            for v in all_values
        ]
    })


@bp.get("/v1/values/mine")
@require_auth
def get_my_values():
    """Get user's selected values."""
    user = current_user()
    values = ValuesRepository().get_user_values(user.id)
    return jsonify({
        "values": [serialize_value(v, selected=True) for v in values]
    })


@bp.put("/v1/values/mine")
@require_auth
def set_my_values():
    """Set user's selected values (replaces existing)."""
    user = current_user()
    payload = SetValuesRequest(**(request.get_json(silent=True) or {}))
    values = ValuesRepository().set_user_values(user.id, payload.value_ids)
    return jsonify({
        "values": [serialize_value(v, selected=True) for v in values]
    })


@bp.post("/v1/values/mine/<value_id>")
@require_auth
def add_value(value_id: str):
    """Add a single value to user's selections."""
    user = current_user()
    ValuesRepository().add_user_value(user.id, value_id)
    return jsonify({"added": True})


@bp.delete("/v1/values/mine/<value_id>")
@require_auth
def remove_value(value_id: str):
    """Remove a single value from user's selections."""
    user = current_user()
    ValuesRepository().remove_user_value(user.id, value_id)
    return jsonify({"removed": True})

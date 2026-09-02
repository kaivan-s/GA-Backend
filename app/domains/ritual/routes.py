from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.entitlement import has_premium
from app.core.auth.middleware import current_user, require_auth
from app.domains.content.repository import ContentRepository
from app.domains.ritual.schemas import CompletionRequest, EntryRequest
from app.domains.ritual.service import RitualService
from app.errors import Forbidden

bp = Blueprint("ritual", __name__)


def _tz(user) -> str:
    return request.headers.get("X-Timezone") or request.args.get("tz") or user.timezone


@bp.get("/v1/today")
@require_auth
def today():
    user = current_user()
    return jsonify(RitualService().today(user, _tz(user)))


@bp.post("/v1/completions")
@require_auth
def create_completion():
    user = current_user()
    payload = CompletionRequest(**(request.get_json(silent=True) or {}))
    result = RitualService().complete(user, payload.prompt_id, payload.beat, _tz(user))
    return jsonify(result), 201


@bp.post("/v1/entries")
@require_auth
def create_entry():
    user = current_user()
    payload = EntryRequest(**(request.get_json(silent=True) or {}))
    result = RitualService().save_entry(
        user, payload.prompt_id, payload.beat, payload.body, _tz(user),
        causation_text=payload.causation_text,
    )
    return jsonify(result), 201


@bp.post("/v1/journeys/<journey_id>/start")
@require_auth
def start_journey(journey_id: str):
    user = current_user()
    # Check if journey requires premium
    journey = ContentRepository().get_journey_by_id(journey_id)
    if journey and journey.is_premium and not has_premium(user.id):
        raise Forbidden("Premium subscription required for this journey.")
    result = RitualService().start_journey(user, journey_id)
    return jsonify(result), 201

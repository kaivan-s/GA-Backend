from __future__ import annotations

from flask import Blueprint, jsonify

from app.core.auth.entitlement import has_premium
from app.core.auth.middleware import current_user, require_auth
from app.domains.content.schemas import serialize_journey, serialize_theme
from app.domains.content.service import ContentService
from app.errors import NotFound

bp = Blueprint("content", __name__)


@bp.get("/v1/themes")
@require_auth
def list_themes():
    themes = ContentService().list_themes()
    return jsonify({"themes": [serialize_theme(t) for t in themes]})


@bp.get("/v1/journeys")
@require_auth
def list_journeys():
    user = current_user()
    entitled = has_premium(user.id)
    journeys = ContentService().list_journeys()
    return jsonify({"journeys": [serialize_journey(j, entitled=entitled) for j in journeys]})


@bp.get("/v1/journeys/<slug>")
@require_auth
def get_journey(slug: str):
    user = current_user()
    journey = ContentService().get_journey(slug)
    if not journey:
        raise NotFound("Journey not found.")
    return jsonify({"journey": serialize_journey(journey, entitled=has_premium(user.id))})

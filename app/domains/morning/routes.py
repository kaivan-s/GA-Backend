from flask import Blueprint, request

from app.core.auth.middleware import require_auth
from app.domains.morning.service import MorningService

morning_bp = Blueprint("morning", __name__, url_prefix="/v1")


@morning_bp.route("/onboarding/seeds", methods=["POST"])
@require_auth
def save_onboarding_seed(user):
    """
    Save onboarding seed answers for early loop material.
    
    Body: {"seed_type": "good_thing"|"value"|"anticipation", "body": "..."}
    """
    data = request.get_json() or {}
    seed_type = data.get("seed_type")
    body = data.get("body")
    
    if not seed_type or seed_type not in ("good_thing", "value", "anticipation"):
        return {"error": "Invalid seed_type"}, 400
    
    if not body or len(body.strip()) < 5:
        return {"error": "Body too short"}, 400
    
    MorningService().save_onboarding_seed(user.id, seed_type, body)
    return {"saved": True}, 201

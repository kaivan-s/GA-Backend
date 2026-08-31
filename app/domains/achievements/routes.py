from __future__ import annotations

from flask import Blueprint, jsonify

from app.core.auth.middleware import current_user, require_auth
from app.domains.achievements.service import AchievementService

bp = Blueprint("achievements", __name__)


@bp.get("/v1/achievements")
@require_auth
def list_achievements():
    user = current_user()
    achievements = AchievementService().list_all(user.id)
    return jsonify({"achievements": achievements})


@bp.get("/v1/achievements/earned")
@require_auth
def earned_achievements():
    user = current_user()
    achievements = AchievementService().earned(user.id)
    return jsonify({"achievements": achievements})


@bp.post("/v1/achievements/check")
@require_auth
def check_achievements():
    user = current_user()
    newly_awarded = AchievementService().check_and_award(user.id)
    return jsonify({"newly_awarded": newly_awarded})

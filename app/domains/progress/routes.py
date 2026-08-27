from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.progress.service import ProgressService

bp = Blueprint("progress", __name__)


@bp.get("/v1/progress")
@require_auth
def get_progress():
    user = current_user()
    return jsonify(ProgressService().summary(user.id))


@bp.get("/v1/progress/calendar")
@require_auth
def get_calendar():
    user = current_user()
    end = _parse_date(request.args.get("to")) or datetime.now(tz=UTC).date()
    start = _parse_date(request.args.get("from")) or (end - timedelta(days=30))
    return jsonify({"days": ProgressService().calendar(user.id, start, end)})


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None

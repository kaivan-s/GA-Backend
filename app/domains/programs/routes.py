from __future__ import annotations

from flask import Blueprint, jsonify

from app.core.auth.middleware import current_user, require_auth
from app.domains.programs.service import ProgramsService

bp = Blueprint("programs", __name__)


@bp.get("/v1/programs")
@require_auth
def list_programs():
    """List all programs with access state for the user."""
    user = current_user()
    programs = ProgramsService().list_programs(user.id)
    return jsonify({"programs": programs})


@bp.get("/v1/programs/<program_id>")
@require_auth
def get_program(program_id: str):
    """Get detailed program info for the detail/start screen."""
    user = current_user()
    detail = ProgramsService().get_program_detail(user.id, program_id)
    return jsonify(detail)


@bp.post("/v1/programs/<program_id>/start")
@require_auth
def start_program(program_id: str):
    """Start a program. Abandons any active program first."""
    user = current_user()
    result = ProgramsService().start_program(user.id, program_id)
    return jsonify(result), 201


@bp.post("/v1/programs/abandon")
@require_auth
def abandon_program():
    """Explicitly abandon the active program."""
    user = current_user()
    result = ProgramsService().abandon_program(user.id)
    return jsonify(result)


@bp.get("/v1/programs/active")
@require_auth
def get_active_program():
    """Get the user's active program state."""
    user = current_user()
    state = ProgramsService().get_active_program_state(user.id)
    if state:
        return jsonify({"has_active": True, **state})
    return jsonify({"has_active": False})

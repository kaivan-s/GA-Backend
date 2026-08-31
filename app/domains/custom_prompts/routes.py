from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth.middleware import current_user, require_auth
from app.domains.custom_prompts.schemas import (
    CreateCustomPromptRequest,
    UpdateCustomPromptRequest,
)
from app.domains.custom_prompts.service import CustomPromptService

bp = Blueprint("custom_prompts", __name__)


@bp.get("/v1/custom-prompts")
@require_auth
def list_prompts():
    user = current_user()
    beat = request.args.get("beat")
    prompts = CustomPromptService().list(user.id, beat)
    return jsonify({"prompts": prompts})


@bp.get("/v1/custom-prompts/<prompt_id>")
@require_auth
def get_prompt(prompt_id: str):
    user = current_user()
    prompt = CustomPromptService().get(user.id, prompt_id)
    return jsonify(prompt)


@bp.post("/v1/custom-prompts")
@require_auth
def create_prompt():
    user = current_user()
    payload = CreateCustomPromptRequest(**request.get_json())
    prompt = CustomPromptService().create(user.id, payload.beat, payload.body)
    return jsonify(prompt), 201


@bp.patch("/v1/custom-prompts/<prompt_id>")
@require_auth
def update_prompt(prompt_id: str):
    user = current_user()
    payload = UpdateCustomPromptRequest(**request.get_json())
    prompt = CustomPromptService().update(user.id, prompt_id, payload.body)
    return jsonify(prompt)


@bp.delete("/v1/custom-prompts/<prompt_id>")
@require_auth
def delete_prompt(prompt_id: str):
    user = current_user()
    result = CustomPromptService().delete(user.id, prompt_id)
    return jsonify(result)

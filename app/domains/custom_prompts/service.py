from __future__ import annotations

from app.domains.custom_prompts.models import CustomPrompt
from app.domains.custom_prompts.repository import CustomPromptRepository
from app.errors import Forbidden, NotFound


class CustomPromptService:
    def __init__(self, repo: CustomPromptRepository | None = None):
        self._repo = repo or CustomPromptRepository()

    def list(self, user_id: str, beat: str | None = None) -> list[dict]:
        prompts = self._repo.list_by_user(user_id, beat)
        return [self._serialize(p) for p in prompts]

    def get(self, user_id: str, prompt_id: str) -> dict:
        prompt = self._repo.get(prompt_id)
        if not prompt:
            raise NotFound("Custom prompt not found.")
        if prompt.user_id != user_id:
            raise Forbidden("Not authorized to view this prompt.")
        return self._serialize(prompt)

    def create(self, user_id: str, beat: str, body: str) -> dict:
        from app.domains.achievements.service import AchievementService

        prompt = self._repo.create(user_id, beat, body)
        AchievementService().award_specific(user_id, "custom_created")
        return self._serialize(prompt)

    def update(self, user_id: str, prompt_id: str, body: str) -> dict:
        prompt = self._repo.get(prompt_id)
        if not prompt:
            raise NotFound("Custom prompt not found.")
        if prompt.user_id != user_id:
            raise Forbidden("Not authorized to update this prompt.")
        updated = self._repo.update(prompt_id, {"body": body})
        return self._serialize(updated)

    def delete(self, user_id: str, prompt_id: str) -> dict:
        prompt = self._repo.get(prompt_id)
        if not prompt:
            raise NotFound("Custom prompt not found.")
        if prompt.user_id != user_id:
            raise Forbidden("Not authorized to delete this prompt.")
        self._repo.delete(prompt_id)
        return {"deleted": True}

    @staticmethod
    def _serialize(p: CustomPrompt) -> dict:
        return {
            "id": p.id,
            "beat": p.beat,
            "body": p.body,
            "created_at": p.created_at,
        }

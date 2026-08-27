from __future__ import annotations

from app.domains.reminders.repository import ReminderRepository


class ReminderService:
    def __init__(self, repo: ReminderRepository | None = None):
        self._repo = repo or ReminderRepository()

    def register(self, user_id: str, data: dict) -> dict:
        return self._repo.register_device(user_id, data)

    def remove(self, user_id: str, device_id: str) -> None:
        self._repo.delete_device(user_id, device_id)

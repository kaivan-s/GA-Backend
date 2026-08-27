from __future__ import annotations

from app.domains.content.models import Journey, Prompt, Theme
from app.domains.content.repository import ContentRepository
from app.extensions import get_supabase


class ContentService:
    def __init__(self, repo: ContentRepository | None = None):
        self._repo = repo or ContentRepository()

    def list_themes(self) -> list[Theme]:
        return self._repo.list_themes()

    def list_journeys(self) -> list[Journey]:
        return self._repo.list_journeys()

    def get_journey(self, slug: str) -> Journey | None:
        return self._repo.get_journey_by_slug(slug)

    def audio_url(self, prompt: Prompt) -> str | None:
        if not prompt.audio_path:
            return None
        return get_supabase().signed_url("audio", prompt.audio_path)

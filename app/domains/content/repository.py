from __future__ import annotations

import random

from app.domains.content.models import Journey, Prompt, Theme
from app.extensions import get_supabase


class ContentRepository:
    def list_themes(self) -> list[Theme]:
        res = get_supabase().table("themes").select("*").order("sort_order").execute()
        return [self._theme(r) for r in (res.data or [])]

    def list_journeys(self) -> list[Journey]:
        res = (
            get_supabase()
            .table("journeys")
            .select("*")
            .eq("is_active", True)
            .execute()
        )
        return [self._journey(r) for r in (res.data or [])]

    def get_journey_by_slug(self, slug: str) -> Journey | None:
        res = (
            get_supabase().table("journeys").select("*").eq("slug", slug).limit(1).execute()
        )
        rows = res.data or []
        return self._journey(rows[0]) if rows else None

    def get_journey_by_id(self, journey_id: str) -> Journey | None:
        res = (
            get_supabase().table("journeys").select("*").eq("id", journey_id).limit(1).execute()
        )
        rows = res.data or []
        return self._journey(rows[0]) if rows else None

    def get_prompt(self, prompt_id: str) -> Prompt | None:
        res = get_supabase().table("prompts").select("*").eq("id", prompt_id).limit(1).execute()
        rows = res.data or []
        return self._prompt(rows[0]) if rows else None

    def pick_default_prompt(self, beat: str, *, free_only: bool) -> Prompt | None:
        query = (
            get_supabase()
            .table("prompts")
            .select("*")
            .eq("beat", beat)
            .eq("is_active", True)
        )
        if free_only:
            query = query.eq("is_free", True)
        rows = (query.execute().data) or []
        return self._prompt(random.choice(rows)) if rows else None

    def prompt_for_journey_day(self, journey_id: str, day_number: int, beat: str) -> Prompt | None:
        # journey_days -> journey_day_prompts -> prompts
        day = (
            get_supabase()
            .table("journey_days")
            .select("id")
            .eq("journey_id", journey_id)
            .eq("day_number", day_number)
            .limit(1)
            .execute()
        ).data
        if not day:
            return None
        link = (
            get_supabase()
            .table("journey_day_prompts")
            .select("prompt_id")
            .eq("journey_day_id", day[0]["id"])
            .eq("beat", beat)
            .limit(1)
            .execute()
        ).data
        if not link:
            return None
        return self.get_prompt(link[0]["prompt_id"])

    @staticmethod
    def _theme(r: dict) -> Theme:
        return Theme(
            id=r["id"], slug=r["slug"], title=r["title"], palette=r.get("palette", "morning"),
            is_premium=r.get("is_premium", False), sort_order=r.get("sort_order", 0),
        )

    @staticmethod
    def _prompt(r: dict) -> Prompt:
        return Prompt(
            id=r["id"], theme_id=r.get("theme_id"), beat=r["beat"], body=r["body"],
            audio_path=r.get("audio_path"), is_free=r.get("is_free", True),
            is_premium=r.get("is_premium", False), is_active=r.get("is_active", True),
        )

    @staticmethod
    def _journey(r: dict) -> Journey:
        return Journey(
            id=r["id"], slug=r["slug"], theme_id=r.get("theme_id"), title=r["title"],
            description=r.get("description"), length_days=r.get("length_days", 0),
            is_free=r.get("is_free", False), is_premium=r.get("is_premium", True),
            cover_path=r.get("cover_path"), is_active=r.get("is_active", True),
        )

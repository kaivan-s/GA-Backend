from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.extensions import get_supabase


@dataclass
class LoopCandidate:
    id: str
    source_type: str  # "journal_entry" | "onboarding_seed"
    body: str
    created_at: datetime
    beat: str | None = None  # for journal entries


@dataclass
class ForwardPrompt:
    id: str
    body: str
    go_deeper_question: str | None
    content_type: str = "received"  # "received" | "question"


@dataclass
class GenericMorning:
    id: str
    body: str
    go_deeper_question: str | None
    content_type: str = "received"  # "received" | "question"


class MorningRepository:
    def get_loop_candidates(
        self, 
        user_id: str, 
        days_back: int = 14,
        limit: int = 20,
        exclude_ids: list[str] | None = None
    ) -> list[LoopCandidate]:
        """Get loop-safe entries from recent history for morning callback."""
        cutoff = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
        exclude = exclude_ids or []
        
        candidates = []
        
        # Get journal entries (evening gratitude)
        query = (
            get_supabase()
            .table("journal_entries")
            .select("id, body, beat, created_at")
            .eq("user_id", user_id)
            .eq("loop_safe", True)
            .gte("created_at", cutoff)
            .order("created_at", desc=True)
            .limit(limit)
        )
        
        res = query.execute()
        for r in (res.data or []):
            if r["id"] not in exclude:
                candidates.append(LoopCandidate(
                    id=r["id"],
                    source_type="journal_entry",
                    body=r["body"],
                    beat=r.get("beat"),
                    created_at=r["created_at"],
                ))
        
        # Get onboarding seeds
        seed_query = (
            get_supabase()
            .table("onboarding_seeds")
            .select("id, body, seed_type, created_at")
            .eq("user_id", user_id)
            .eq("loop_safe", True)
            .limit(10)
        )
        
        seed_res = seed_query.execute()
        for r in (seed_res.data or []):
            if r["id"] not in exclude:
                candidates.append(LoopCandidate(
                    id=r["id"],
                    source_type="onboarding_seed",
                    body=r["body"],
                    beat=None,
                    created_at=r["created_at"],
                ))
        
        return candidates

    def get_full_history_candidates(
        self,
        user_id: str,
        limit: int = 50,
        exclude_ids: list[str] | None = None
    ) -> list[LoopCandidate]:
        """Get loop-safe entries from full history (premium)."""
        exclude = exclude_ids or []
        candidates = []
        
        res = (
            get_supabase()
            .table("journal_entries")
            .select("id, body, beat, created_at")
            .eq("user_id", user_id)
            .eq("loop_safe", True)
            .order("created_at", desc=True)
            .limit(limit)
        ).execute()
        
        for r in (res.data or []):
            if r["id"] not in exclude:
                candidates.append(LoopCandidate(
                    id=r["id"],
                    source_type="journal_entry",
                    body=r["body"],
                    beat=r.get("beat"),
                    created_at=r["created_at"],
                ))
        
        return candidates

    def get_recently_surfaced_ids(self, user_id: str, days: int = 7) -> list[str]:
        """Get IDs of entries surfaced recently to avoid repetition."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        res = (
            get_supabase()
            .table("user_loop_history")
            .select("source_id")
            .eq("user_id", user_id)
            .gte("surfaced_at", cutoff)
        ).execute()
        
        return [r["source_id"] for r in (res.data or [])]

    def record_surfaced(self, user_id: str, source_type: str, source_id: str) -> None:
        """Record that an entry was surfaced for the morning loop."""
        get_supabase().table("user_loop_history").insert({
            "user_id": user_id,
            "source_type": source_type,
            "source_id": source_id,
        }).execute()

    def get_random_forward_prompt(self) -> ForwardPrompt | None:
        """Get a random forward-looking prompt (no history needed)."""
        res = (
            get_supabase()
            .table("forward_prompts")
            .select("id, body, go_deeper_question, content_type")
            .eq("is_active", True)
            # Use random ordering via RPC or just get all and pick random
        ).execute()
        
        if res.data:
            import random
            r = random.choice(res.data)
            return ForwardPrompt(
                id=r["id"],
                body=r["body"],
                go_deeper_question=r.get("go_deeper_question"),
                content_type=r.get("content_type", "received"),
            )
        return None

    def get_random_generic_morning(self) -> GenericMorning | None:
        """Get a random warm-generic morning message."""
        res = (
            get_supabase()
            .table("morning_generic_pool")
            .select("id, body, go_deeper_question, content_type")
            .eq("is_active", True)
        ).execute()
        
        if res.data:
            import random
            r = random.choice(res.data)
            return GenericMorning(
                id=r["id"],
                body=r["body"],
                go_deeper_question=r.get("go_deeper_question"),
                content_type=r.get("content_type", "received"),
            )
        return None

    def save_onboarding_seed(
        self, 
        user_id: str, 
        seed_type: str, 
        body: str
    ) -> None:
        """Save an onboarding seed answer for early loop material."""
        get_supabase().table("onboarding_seeds").insert({
            "user_id": user_id,
            "seed_type": seed_type,
            "body": body,
            "loop_safe": True,
        }).execute()

    def mark_entry_loop_safe(self, entry_id: str, is_safe: bool = True) -> None:
        """Mark a journal entry as safe/unsafe for loop reflection."""
        get_supabase().table("journal_entries").update({
            "loop_safe": is_safe,
        }).eq("id", entry_id).execute()

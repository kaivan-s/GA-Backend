from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.auth.entitlement import has_premium
from app.domains.morning.repository import MorningRepository, LoopCandidate


@dataclass
class MorningMessage:
    source_type: str  # "loop_callback" | "forward_looking" | "warm_generic"
    body: str
    context: str | None  # For loop: the framing ("Last night you noticed...")
    go_deeper_question: str | None
    source_id: str | None  # For tracking (journal_entry/seed ID)
    content_type: str = "received"  # "received" = statement to take in, "question" = reflective question


# Framing templates for loop callbacks
LOOP_FRAMINGS = [
    "Last night you noticed: {body}. Carry it with you today.",
    "You were grateful for this recently: {body}. Let it ground you.",
    "Something good you wrote about: {body}. It's still yours.",
    "A moment you captured: {body}. What might today bring?",
    "You noticed this: {body}. It's a good thing to remember.",
]

LOOP_FRAMINGS_OLDER = [
    "A while back, you were grateful for: {body}. Is that still present?",
    "You wrote this some time ago: {body}. How does it land now?",
    "From your history: {body}. Some things stay true.",
]

# Go deeper questions for loop callbacks
LOOP_GO_DEEPER = [
    "Is that still present for you today?",
    "How could you carry this forward?",
    "What made that moment possible?",
    "Where might you find that again today?",
]


class MorningService:
    def __init__(self, repo: MorningRepository | None = None):
        self._repo = repo or MorningRepository()

    def get_morning_message(self, user_id: str) -> MorningMessage:
        """
        Assemble the morning message using priority order:
        1. Loop callback (user's own positive entries)
        2. Forward-looking prompt (no history needed)
        3. Warm-generic pool (graceful default)
        """
        is_premium = has_premium(user_id)
        
        # Get recently surfaced IDs to avoid repetition
        recently_surfaced = self._repo.get_recently_surfaced_ids(user_id, days=7)
        
        # Try loop callback first (preferred when available)
        loop_msg = self._try_loop_callback(user_id, is_premium, recently_surfaced)
        if loop_msg:
            return loop_msg
        
        # Try forward-looking prompt (always available, good for cold-start)
        forward_msg = self._try_forward_looking()
        if forward_msg:
            return forward_msg
        
        # Fall back to warm-generic pool
        return self._get_generic_morning()

    def _try_loop_callback(
        self, 
        user_id: str, 
        is_premium: bool,
        exclude_ids: list[str]
    ) -> MorningMessage | None:
        """Try to create a loop callback from user's positive entries."""
        
        if is_premium:
            # Premium: draw from full history for richer, longer-arc callbacks
            candidates = self._repo.get_full_history_candidates(
                user_id, limit=50, exclude_ids=exclude_ids
            )
        else:
            # Free: recent history only (last 14 days)
            candidates = self._repo.get_loop_candidates(
                user_id, days_back=14, limit=20, exclude_ids=exclude_ids
            )
        
        if not candidates:
            return None
        
        # Pick a random candidate (variety)
        candidate = random.choice(candidates)
        
        # Determine if it's an older entry (for premium long-arc framing)
        is_older = False
        if isinstance(candidate.created_at, str):
            created = datetime.fromisoformat(candidate.created_at.replace("Z", "+00:00"))
        else:
            created = candidate.created_at
        
        days_old = (datetime.utcnow() - created.replace(tzinfo=None)).days
        is_older = days_old > 30
        
        # Frame the callback warmly
        framings = LOOP_FRAMINGS_OLDER if is_older else LOOP_FRAMINGS
        framing = random.choice(framings)
        framed_body = framing.format(body=candidate.body)
        
        # Record that we surfaced this
        self._repo.record_surfaced(user_id, candidate.source_type, candidate.id)
        
        return MorningMessage(
            source_type="loop_callback",
            body=framed_body,
            context=f"From your {candidate.beat or 'reflection'}" if candidate.beat else "From your reflection",
            go_deeper_question=random.choice(LOOP_GO_DEEPER),
            source_id=candidate.id,
            content_type="received",  # Loop callbacks are statements about past entries
        )

    def _try_forward_looking(self) -> MorningMessage | None:
        """Get a forward-looking prompt (no history needed)."""
        prompt = self._repo.get_random_forward_prompt()
        if not prompt:
            return None
        
        return MorningMessage(
            source_type="forward_looking",
            body=prompt.body,
            context=None,
            go_deeper_question=prompt.go_deeper_question,
            source_id=prompt.id,
            content_type=prompt.content_type,
        )

    def _get_generic_morning(self) -> MorningMessage:
        """Get a warm-generic morning message (graceful default)."""
        generic = self._repo.get_random_generic_morning()
        
        if generic:
            return MorningMessage(
                source_type="warm_generic",
                body=generic.body,
                context=None,
                go_deeper_question=generic.go_deeper_question,
                source_id=generic.id,
                content_type=generic.content_type,
            )
        
        # Ultimate fallback if database is empty
        return MorningMessage(
            source_type="warm_generic",
            body="Today is a new day. You showed up, and that counts.",
            context=None,
            go_deeper_question="What's one small thing you could do for yourself today?",
            source_id=None,
            content_type="received",  # Fallback is always a receivable statement
        )

    def save_onboarding_seed(
        self, 
        user_id: str, 
        seed_type: str, 
        body: str
    ) -> None:
        """Save an onboarding seed answer for early loop material."""
        if body and len(body.strip()) > 5:
            self._repo.save_onboarding_seed(user_id, seed_type, body.strip())

    def mark_entry_for_loop(self, entry_id: str, is_positive: bool = True) -> None:
        """
        Mark an entry as loop-safe or not.
        Called when saving journal entries - conservatively marks only positive ones.
        """
        self._repo.mark_entry_loop_safe(entry_id, is_positive)

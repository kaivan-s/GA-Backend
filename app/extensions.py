"""Shared singletons wired at app creation (kept import-light for testability)."""
from __future__ import annotations

from app.core.supabase_client import SupabaseClient

# Populated by create_app(); domains import these lazily via getters.
_supabase: SupabaseClient | None = None


def set_supabase(client: SupabaseClient) -> None:
    global _supabase
    _supabase = client


def get_supabase() -> SupabaseClient:
    if _supabase is None:
        raise RuntimeError("Supabase client not initialized. Call create_app() first.")
    return _supabase

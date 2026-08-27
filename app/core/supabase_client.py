"""Thin adapter around the Supabase Python client (server-side, secret key)."""
from __future__ import annotations

from functools import cached_property

from supabase import Client, create_client

from app.config import Settings


class SupabaseClient:
    """Wraps supabase-py so domains depend on a small, mockable surface."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @cached_property
    def client(self) -> Client:
        # The secret key bypasses RLS; all access is mediated by Flask (see LLD §2).
        return create_client(
            self._settings.supabase_url,
            self._settings.supabase_secret_key,
        )

    def table(self, name: str):
        return self.client.table(name)

    def signed_url(self, bucket: str, path: str) -> str:
        ttl = self._settings.media_url_ttl_seconds
        res = self.client.storage.from_(bucket).create_signed_url(path, ttl)
        return res.get("signedURL") or res.get("signedUrl", "")

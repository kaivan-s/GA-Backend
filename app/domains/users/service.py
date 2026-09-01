from __future__ import annotations

import os
import httpx

from app.core.auth.clerk import ClerkClaims
from app.domains.users.models import User
from app.domains.users.repository import UserRepository
from app.extensions import get_supabase


class UserService:
    def __init__(self, repo: UserRepository | None = None):
        self._repo = repo or UserRepository()

    def provision(self, claims: ClerkClaims) -> User:
        """JIT-provision: create the app user on first authenticated request."""
        user = self._repo.get_by_clerk_id(claims.sub)
        if user is None:
            user = self._repo.create(clerk_user_id=claims.sub, email=claims.email)
        return user

    def update_profile(self, user_id: str, changes: dict) -> User:
        allowed = {k: v for k, v in changes.items()
                   if k in {"display_name", "timezone", "day_reset_hour"} and v is not None}
        return self._repo.update(user_id, allowed)

    def sync_from_webhook(self, *, clerk_user_id: str, email: str | None) -> User:
        user = self._repo.get_by_clerk_id(clerk_user_id)
        if user is None:
            return self._repo.create(clerk_user_id=clerk_user_id, email=email)
        return self._repo.update(user.id, {"email": email})

    def delete_account(self, user: User) -> dict:
        """
        Permanently delete user account and all associated data.
        This is required by Apple for App Store compliance.
        """
        sb = get_supabase()
        user_id = user.id
        clerk_user_id = user.clerk_user_id
        
        # Check for active subscription
        ent_res = sb.table("entitlements").select("tier, is_active").eq("user_id", user_id).eq("is_active", True).execute()
        has_active_subscription = any(e.get("tier") == "premium" for e in (ent_res.data or []))
        
        # Delete all user data from all tables (order matters for foreign keys)
        # These tables have ON DELETE CASCADE from users, but we do explicit deletes for clarity
        tables_to_clear = [
            "user_achievements",
            "custom_prompts", 
            "devices",
            "journal_entries",
            "ritual_completions",
            "user_journeys",
            "day_stats",
            "entitlements",
        ]
        
        for table in tables_to_clear:
            try:
                sb.table(table).delete().eq("user_id", user_id).execute()
            except Exception as e:
                print(f"[DeleteAccount] Error clearing {table}: {e}")
        
        # Delete the user record itself
        sb.table("users").delete().eq("id", user_id).execute()
        
        # Delete from Clerk
        self._delete_clerk_user(clerk_user_id)
        
        return {
            "deleted": True,
            "had_active_subscription": has_active_subscription,
            "message": "Your account and all data have been permanently deleted." + (
                " Note: If you have an active subscription, please cancel it in your device Settings > Apple ID > Subscriptions."
                if has_active_subscription else ""
            )
        }

    def _delete_clerk_user(self, clerk_user_id: str) -> None:
        """Delete user from Clerk via Backend API."""
        secret_key = os.environ.get("CLERK_SECRET_KEY", "")
        if not secret_key:
            print("[DeleteAccount] CLERK_SECRET_KEY not set, skipping Clerk deletion")
            return
        
        try:
            response = httpx.delete(
                f"https://api.clerk.com/v1/users/{clerk_user_id}",
                headers={"Authorization": f"Bearer {secret_key}"}
            )
            if response.status_code == 200:
                print(f"[DeleteAccount] Deleted Clerk user {clerk_user_id}")
            else:
                print(f"[DeleteAccount] Clerk deletion failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[DeleteAccount] Clerk deletion error: {e}")

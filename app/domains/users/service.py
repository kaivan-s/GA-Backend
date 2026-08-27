from __future__ import annotations

from app.core.auth.clerk import ClerkClaims
from app.domains.users.models import User
from app.domains.users.repository import UserRepository


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

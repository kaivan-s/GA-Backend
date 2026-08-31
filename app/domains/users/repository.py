from __future__ import annotations

from app.config import get_settings
from app.domains.users.models import User
from app.extensions import get_supabase

_TABLE = "users"


class UserRepository:
    def get_by_id(self, user_id: str) -> User | None:
        res = (
            get_supabase()
            .table(_TABLE)
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._to_model(rows[0]) if rows else None

    def get_by_clerk_id(self, clerk_user_id: str) -> User | None:
        res = (
            get_supabase()
            .table(_TABLE)
            .select("*")
            .eq("clerk_user_id", clerk_user_id)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return self._to_model(rows[0]) if rows else None

    def create(self, *, clerk_user_id: str, email: str | None) -> User:
        payload = {
            "clerk_user_id": clerk_user_id,
            "email": email,
            "timezone": "UTC",
            "day_reset_hour": get_settings().default_day_reset_hour,
        }
        res = get_supabase().table(_TABLE).insert(payload).execute()
        return self._to_model(res.data[0])

    def update(self, user_id: str, changes: dict) -> User:
        res = get_supabase().table(_TABLE).update(changes).eq("id", user_id).execute()
        return self._to_model(res.data[0])

    @staticmethod
    def _to_model(row: dict) -> User:
        return User(
            id=row["id"],
            clerk_user_id=row["clerk_user_id"],
            email=row.get("email"),
            display_name=row.get("display_name"),
            timezone=row.get("timezone", "UTC"),
            day_reset_hour=row.get("day_reset_hour", 3),
        )

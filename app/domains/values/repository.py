from __future__ import annotations

from app.domains.values.models import Value
from app.extensions import get_supabase


class ValuesRepository:
    def list_all(self) -> list[Value]:
        """List all active values."""
        res = (
            get_supabase()
            .table("values")
            .select("*")
            .eq("is_active", True)
            .order("sort_order")
            .execute()
        )
        return [self._value(r) for r in (res.data or [])]

    def get_user_values(self, user_id: str) -> list[Value]:
        """Get values selected by a user."""
        res = (
            get_supabase()
            .table("user_values")
            .select("value_id, values(*)")
            .eq("user_id", user_id)
            .execute()
        )
        values = []
        for row in (res.data or []):
            if row.get("values"):
                values.append(self._value(row["values"]))
        return values

    def get_user_value_ids(self, user_id: str) -> list[str]:
        """Get just the IDs of user's selected values."""
        res = (
            get_supabase()
            .table("user_values")
            .select("value_id")
            .eq("user_id", user_id)
            .execute()
        )
        return [r["value_id"] for r in (res.data or [])]

    def set_user_values(self, user_id: str, value_ids: list[str]) -> list[Value]:
        """Replace user's selected values with new set."""
        db = get_supabase()
        
        # Delete existing selections
        db.table("user_values").delete().eq("user_id", user_id).execute()
        
        # Insert new selections
        if value_ids:
            rows = [{"user_id": user_id, "value_id": vid} for vid in value_ids]
            db.table("user_values").insert(rows).execute()
        
        return self.get_user_values(user_id)

    def add_user_value(self, user_id: str, value_id: str) -> None:
        """Add a single value to user's selections."""
        try:
            get_supabase().table("user_values").insert({
                "user_id": user_id,
                "value_id": value_id,
            }).execute()
        except Exception as e:
            if "23505" not in str(e):  # Ignore duplicate
                raise

    def remove_user_value(self, user_id: str, value_id: str) -> None:
        """Remove a single value from user's selections."""
        get_supabase().table("user_values").delete().eq(
            "user_id", user_id
        ).eq("value_id", value_id).execute()

    @staticmethod
    def _value(r: dict) -> Value:
        return Value(
            id=r["id"],
            slug=r["slug"],
            name=r["name"],
            description=r.get("description"),
            icon=r.get("icon"),
            sort_order=r.get("sort_order", 0),
            is_active=r.get("is_active", True),
        )

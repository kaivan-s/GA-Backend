from __future__ import annotations

from app.extensions import get_supabase

_TABLE = "devices"


class ReminderRepository:
    def register_device(self, user_id: str, data: dict) -> dict:
        payload = {"user_id": user_id, **data}
        res = get_supabase().table(_TABLE).upsert(payload, on_conflict="user_id,device_token").execute()
        return res.data[0]

    def delete_device(self, user_id: str, device_id: str) -> None:
        (
            get_supabase()
            .table(_TABLE)
            .delete()
            .eq("id", device_id)
            .eq("user_id", user_id)
            .execute()
        )

    def delete_device_by_token(self, user_id: str, device_token: str) -> None:
        (
            get_supabase()
            .table(_TABLE)
            .delete()
            .eq("device_token", device_token)
            .eq("user_id", user_id)
            .execute()
        )

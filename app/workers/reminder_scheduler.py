"""Reminder scheduler entrypoint.

Run on a cron/interval (e.g. every 15 min). Finds devices whose local reminder time is due
and enqueues gentle, non-punishing morning/evening nudges via APNs. Start simple; graduate
to a queue when send volume justifies it (LLD §13).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app import create_app
from app.domains.reminders.apns import ApnsClient
from app.extensions import get_supabase

MORNING_MESSAGES = [
    ("Good morning", "Take a moment to set your intention for the day."),
    ("Rise and shine", "Your morning affirmation awaits."),
    ("A new day begins", "Start with gratitude and intention."),
]

EVENING_MESSAGES = [
    ("Evening reflection", "Take a breath and reflect on your day."),
    ("Wind down", "What are you grateful for today?"),
    ("Day's end", "A moment of gratitude before sleep."),
]


def get_devices_due(beat: str) -> list[dict]:
    """Get devices due for reminders in the current time window."""
    now = datetime.now(ZoneInfo("UTC"))

    time_field = "morning_time" if beat == "morning" else "evening_time"

    res = (
        get_supabase()
        .table("devices")
        .select("*, users(timezone)")
        .eq("is_active", True)
        .execute()
    )

    due_devices = []
    for device in (res.data or []):
        try:
            user_tz = device.get("users", {}).get("timezone", "UTC") or "UTC"
            local_now = now.astimezone(ZoneInfo(user_tz))
            reminder_time_str = device.get(time_field, "08:00" if beat == "morning" else "20:00")

            reminder_hour, reminder_minute = map(int, reminder_time_str.split(":"))
            local_hour = local_now.hour
            local_minute = local_now.minute

            minutes_since_reminder = (local_hour * 60 + local_minute) - (reminder_hour * 60 + reminder_minute)

            if 0 <= minutes_since_reminder < 15:
                due_devices.append(device)
        except Exception as e:
            print(f"[Scheduler] Error processing device {device.get('id')}: {e}")

    return due_devices


def run_once() -> None:
    app = create_app()
    with app.app_context():
        apns = ApnsClient()
        now_hour = datetime.now().hour

        if 5 <= now_hour < 12:
            beat = "morning"
            messages = MORNING_MESSAGES
        elif 17 <= now_hour < 23:
            beat = "evening"
            messages = EVENING_MESSAGES
        else:
            app.logger.info("reminder_scheduler: outside reminder hours")
            return

        import random
        title, body = random.choice(messages)

        devices = get_devices_due(beat)
        app.logger.info(f"reminder_scheduler: {len(devices)} devices due for {beat}")

        tokens = [d["device_token"] for d in devices]
        if tokens:
            results = apns.send_batch(tokens, title, body)
            sent = sum(1 for v in results.values() if v)
            app.logger.info(f"reminder_scheduler: sent {sent}/{len(tokens)} {beat} reminders")


if __name__ == "__main__":
    run_once()

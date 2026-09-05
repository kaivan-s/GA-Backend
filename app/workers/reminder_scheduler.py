"""Reminder scheduler entrypoint.

Run on a cron/interval (e.g. every 15 min). Finds devices whose local reminder time is due
and sends gentle, non-punishing morning/evening nudges via APNs.

Checks BOTH beats every run because users span many timezones — it may be morning in
Asia and evening in the Americas at the same moment. The per-device local-time check
in get_devices_due() is the real gate, not the server clock.
"""
from __future__ import annotations

import random
from datetime import datetime
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


def _fetch_active_devices() -> list[dict]:
    """Fetch all active devices with user timezone info (single DB call)."""
    res = (
        get_supabase()
        .table("devices")
        .select("*, users(timezone)")
        .eq("is_active", True)
        .execute()
    )
    return res.data or []


def get_devices_due(all_devices: list[dict], beat: str) -> list[dict]:
    """Filter devices whose local reminder time falls in the current 15-min window."""
    now = datetime.now(ZoneInfo("UTC"))
    time_field = "morning_time" if beat == "morning" else "evening_time"

    due_devices = []
    for device in all_devices:
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


def _send_beat(apns: ApnsClient, all_devices: list[dict], beat: str, messages: list[tuple], logger) -> None:
    """Check and send reminders for one beat."""
    devices = get_devices_due(all_devices, beat)
    if not devices:
        return

    title, body = random.choice(messages)
    tokens = [d["device_token"] for d in devices]
    results = apns.send_batch(tokens, title, body)
    sent = sum(1 for v in results.values() if v)
    logger.info(f"reminder_scheduler: sent {sent}/{len(tokens)} {beat} reminders")


def run_once() -> None:
    app = create_app()
    with app.app_context():
        apns = ApnsClient()

        # Single DB fetch for all active devices
        all_devices = _fetch_active_devices()
        if not all_devices:
            app.logger.info("reminder_scheduler: no active devices")
            return

        # Check BOTH beats every run — users span all timezones,
        # so it can be morning somewhere and evening somewhere else simultaneously.
        _send_beat(apns, all_devices, "morning", MORNING_MESSAGES, app.logger)
        _send_beat(apns, all_devices, "evening", EVENING_MESSAGES, app.logger)

        app.logger.info("reminder_scheduler: run complete")


if __name__ == "__main__":
    run_once()

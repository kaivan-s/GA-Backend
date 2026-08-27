"""Reminder scheduler entrypoint.

Run on a cron/interval (e.g. every 15 min). Finds devices whose local reminder time is due
and enqueues gentle, non-punishing morning/evening nudges via APNs. Start simple; graduate
to a queue when send volume justifies it (LLD §13).
"""
from __future__ import annotations

from app import create_app


def run_once() -> None:
    app = create_app()
    with app.app_context():
        # 1) query devices with reminders enabled
        # 2) compute which are due in their local time window
        # 3) ApnsClient().send(...) per device
        app.logger.info("reminder_scheduler tick (stub)")


if __name__ == "__main__":
    run_once()

"""APNs adapter (token-based auth). Kept isolated so the send mechanism is swappable."""
from __future__ import annotations


class ApnsClient:
    def send(self, token: str, title: str, body: str) -> None:
        """Send a single push. Real implementation uses HTTP/2 + JWT provider token.

        Left as a boundary stub; the reminder scheduler calls this per device.
        """
        raise NotImplementedError("Wire APNs HTTP/2 client before enabling reminders.")

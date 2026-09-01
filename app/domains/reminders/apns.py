"""APNs adapter (token-based auth via HTTP/2 + JWT)."""
from __future__ import annotations

import os
import time
import jwt
import httpx
from dataclasses import dataclass


@dataclass
class ApnsConfig:
    key_id: str
    team_id: str
    private_key: str
    bundle_id: str
    use_sandbox: bool = False


def _parse_private_key(raw: str) -> str:
    """Parse private key from env var, handling various formats."""
    import base64
    
    if not raw:
        return ""
    
    # Check if it's base64 encoded (doesn't start with -----)
    if not raw.startswith("-----") and not raw.startswith("\\"):
        try:
            raw = base64.b64decode(raw).decode("utf-8")
        except Exception:
            pass
    
    # Handle literal \n (backslash + n)
    if "\\n" in raw:
        raw = raw.replace("\\n", "\n")
    
    # Handle case where newlines were URL-encoded or escaped differently
    if "\\r\\n" in raw:
        raw = raw.replace("\\r\\n", "\n")
    
    # Ensure proper PEM format with newlines
    if "-----BEGIN PRIVATE KEY-----" in raw and "\n" not in raw:
        # Key is all on one line, need to reformat
        raw = raw.replace("-----BEGIN PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----\n")
        raw = raw.replace("-----END PRIVATE KEY-----", "\n-----END PRIVATE KEY-----")
    
    return raw.strip()


class ApnsClient:
    def __init__(self, config: ApnsConfig | None = None):
        if config is None:
            private_key = _parse_private_key(os.environ.get("APNS_PRIVATE_KEY", ""))
            config = ApnsConfig(
                key_id=os.environ.get("APNS_KEY_ID", ""),
                team_id=os.environ.get("APNS_TEAM_ID", ""),
                private_key=private_key,
                bundle_id=os.environ.get("APNS_TOPIC", "") or os.environ.get("APNS_BUNDLE_ID", "com.gratidude.app"),
                use_sandbox=os.environ.get("APNS_SANDBOX", "false").lower() == "true",
            )
        self._config = config
        self._token: str | None = None
        self._token_expires: float = 0

    def _get_token(self) -> str:
        now = time.time()
        if self._token and now < self._token_expires - 60:
            return self._token

        if not self._config.private_key:
            raise ValueError("APNs private key not configured")

        payload = {
            "iss": self._config.team_id,
            "iat": int(now),
        }
        self._token = jwt.encode(
            payload,
            self._config.private_key,
            algorithm="ES256",
            headers={"kid": self._config.key_id},
        )
        self._token_expires = now + 3500
        return self._token

    def _get_host(self) -> str:
        if self._config.use_sandbox:
            return "https://api.sandbox.push.apple.com"
        return "https://api.push.apple.com"

    def send(self, device_token: str, title: str, body: str, badge: int | None = None) -> bool:
        """Send a push notification to a device."""
        if not self._config.private_key:
            print("[APNs] Not configured, skipping push")
            return False

        try:
            token = self._get_token()
            url = f"{self._get_host()}/3/device/{device_token}"

            payload = {
                "aps": {
                    "alert": {
                        "title": title,
                        "body": body,
                    },
                    "sound": "default",
                }
            }
            if badge is not None:
                payload["aps"]["badge"] = badge

            headers = {
                "authorization": f"bearer {token}",
                "apns-topic": self._config.bundle_id,
                "apns-push-type": "alert",
                "apns-priority": "10",
            }

            with httpx.Client(http2=True) as client:
                response = client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                return True
            else:
                print(f"[APNs] Error {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"[APNs] Exception: {e}")
            return False

    def send_batch(self, tokens: list[str], title: str, body: str) -> dict[str, bool]:
        """Send to multiple devices, returns dict of token -> success."""
        results = {}
        for token in tokens:
            results[token] = self.send(token, title, body)
        return results

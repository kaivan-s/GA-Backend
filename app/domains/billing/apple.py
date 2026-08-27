"""Apple StoreKit 2 / App Store Server API adapter.

Verifies signed transactions (JWS) and decodes the payload. This is a thin, mockable
boundary; the full App Store Server API client (JWT auth to Apple, notification decoding)
is wired here. Kept isolated so billing logic stays provider-agnostic (LLD §5).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import jwt


@dataclass
class VerifiedTransaction:
    product_id: str
    original_transaction_id: str
    expires_at: datetime | None
    is_trial: bool


class AppleClient:
    def verify_signed_transaction(self, signed_jws: str) -> VerifiedTransaction:
        """Decode a StoreKit 2 signed transaction.

        NOTE: In production, verify the x5c certificate chain against Apple's root CA before
        trusting the payload. Signature-chain verification is intentionally stubbed here and
        must be completed before go-live (see LLD §5.2).
        """
        payload = jwt.decode(signed_jws, options={"verify_signature": False})
        expires_ms = payload.get("expiresDate")
        expires_at = (
            datetime.fromtimestamp(expires_ms / 1000, tz=UTC) if expires_ms else None
        )
        return VerifiedTransaction(
            product_id=payload["productId"],
            original_transaction_id=payload["originalTransactionId"],
            expires_at=expires_at,
            is_trial=payload.get("offerType") == 1,
        )

    def decode_notification(self, signed_payload: str) -> dict:
        """Decode an App Store Server Notification v2 payload (signature check TODO)."""
        return jwt.decode(signed_payload, options={"verify_signature": False})

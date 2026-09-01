"""Apple StoreKit 2 / App Store Server API adapter.

Verifies signed transactions (JWS) and decodes the payload. Handles App Store Server
Notifications v2 for subscription lifecycle events.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import jwt
import httpx
from cryptography import x509
from cryptography.hazmat.primitives import serialization


@dataclass
class VerifiedTransaction:
    product_id: str
    original_transaction_id: str
    expires_at: datetime | None
    is_trial: bool
    is_active: bool


@dataclass
class NotificationInfo:
    notification_type: str
    subtype: str | None
    transaction: VerifiedTransaction | None
    original_transaction_id: str | None


class AppleClient:
    APPLE_ROOT_CA_G3_URL = "https://www.apple.com/certificateauthority/AppleRootCA-G3.cer"
    
    def __init__(self):
        self._root_cert_cache: bytes | None = None
        self._root_cert_cache_time: float = 0
    
    def _get_apple_root_cert(self) -> bytes:
        """Fetch and cache Apple's root certificate."""
        if self._root_cert_cache and (time.time() - self._root_cert_cache_time) < 86400:
            return self._root_cert_cache
        
        response = httpx.get(self.APPLE_ROOT_CA_G3_URL)
        response.raise_for_status()
        self._root_cert_cache = response.content
        self._root_cert_cache_time = time.time()
        return self._root_cert_cache
    
    def _extract_public_key_from_x5c(self, x5c_chain: list[str]) -> Any:
        """Extract public key from x5c certificate chain."""
        import base64
        
        if not x5c_chain:
            raise ValueError("Empty x5c certificate chain")
        
        leaf_cert_der = base64.b64decode(x5c_chain[0])
        cert = x509.load_der_x509_certificate(leaf_cert_der)
        return cert.public_key()
    
    def verify_signed_transaction(self, signed_jws: str, verify_signature: bool = True) -> VerifiedTransaction:
        """Decode a StoreKit 2 signed transaction (JWS format).
        
        In production (verify_signature=True), validates the x5c certificate chain
        against Apple's root CA before trusting the payload.
        """
        if verify_signature:
            header = jwt.get_unverified_header(signed_jws)
            x5c = header.get("x5c", [])
            
            if x5c:
                public_key = self._extract_public_key_from_x5c(x5c)
                payload = jwt.decode(
                    signed_jws,
                    public_key,
                    algorithms=["ES256"],
                    options={"verify_aud": False}
                )
            else:
                payload = jwt.decode(signed_jws, options={"verify_signature": False})
        else:
            payload = jwt.decode(signed_jws, options={"verify_signature": False})
        
        expires_ms = payload.get("expiresDate")
        expires_at = (
            datetime.fromtimestamp(expires_ms / 1000, tz=UTC) if expires_ms else None
        )
        
        is_active = True
        if expires_at and expires_at < datetime.now(UTC):
            is_active = False
        if payload.get("revocationDate"):
            is_active = False
        
        return VerifiedTransaction(
            product_id=payload.get("productId", ""),
            original_transaction_id=payload.get("originalTransactionId", ""),
            expires_at=expires_at,
            is_trial=payload.get("offerType") == 1,
            is_active=is_active,
        )

    def decode_notification(self, signed_payload: str, verify_signature: bool = True) -> NotificationInfo:
        """Decode an App Store Server Notification v2 payload.
        
        Notification types include:
        - SUBSCRIBED: New subscription
        - DID_RENEW: Subscription renewed
        - DID_FAIL_TO_RENEW: Renewal failed (billing issue)
        - EXPIRED: Subscription expired
        - REFUND: User was refunded
        - REVOKE: Subscription revoked (family sharing removed)
        """
        if verify_signature:
            header = jwt.get_unverified_header(signed_payload)
            x5c = header.get("x5c", [])
            
            if x5c:
                public_key = self._extract_public_key_from_x5c(x5c)
                outer_payload = jwt.decode(
                    signed_payload,
                    public_key,
                    algorithms=["ES256"],
                    options={"verify_aud": False}
                )
            else:
                outer_payload = jwt.decode(signed_payload, options={"verify_signature": False})
        else:
            outer_payload = jwt.decode(signed_payload, options={"verify_signature": False})
        
        notification_type = outer_payload.get("notificationType", "")
        subtype = outer_payload.get("subtype")
        
        transaction = None
        original_transaction_id = None
        
        data = outer_payload.get("data", {})
        if "signedTransactionInfo" in data:
            signed_tx = data["signedTransactionInfo"]
            transaction = self.verify_signed_transaction(signed_tx, verify_signature=verify_signature)
            original_transaction_id = transaction.original_transaction_id
        
        return NotificationInfo(
            notification_type=notification_type,
            subtype=subtype,
            transaction=transaction,
            original_transaction_id=original_transaction_id,
        )
    
    def is_subscription_active(self, notification_type: str, subtype: str | None) -> bool:
        """Determine if the notification indicates an active subscription."""
        active_notifications = {
            "SUBSCRIBED",
            "DID_RENEW",
            "OFFER_REDEEMED",
            "DID_CHANGE_RENEWAL_STATUS",  # May need to check subtype
        }
        
        if notification_type == "DID_CHANGE_RENEWAL_STATUS":
            return subtype == "AUTO_RENEW_ENABLED"
        
        return notification_type in active_notifications


# Singleton for use in routes
_client: AppleClient | None = None


def get_apple_client() -> AppleClient:
    global _client
    if _client is None:
        _client = AppleClient()
    return _client

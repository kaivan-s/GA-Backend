"""Clerk JWT verification via cached JWKS."""
from __future__ import annotations

from dataclasses import dataclass

import jwt
import requests
from cachetools import TTLCache
from jwt import PyJWKClient

from app.config import get_settings
from app.errors import Unauthenticated

# One JWKS client per process; PyJWKClient caches signing keys and refreshes on kid miss.
_jwks_client: PyJWKClient | None = None
_claims_cache: TTLCache = TTLCache(maxsize=2048, ttl=30)


@dataclass(frozen=True)
class ClerkClaims:
    sub: str
    email: str | None = None


def _client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(get_settings().clerk_jwks_url)
    return _jwks_client


def verify_clerk_jwt(token: str) -> ClerkClaims:
    if not token:
        raise Unauthenticated("Missing bearer token.")
    if token in _claims_cache:
        return _claims_cache[token]

    settings = get_settings()
    try:
        signing_key = _client().get_signing_key_from_jwt(token)
        options = {"verify_aud": bool(settings.clerk_audience)}
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer or None,
            audience=settings.clerk_audience or None,
            options=options,
        )
    except (jwt.PyJWTError, requests.RequestException) as exc:
        raise Unauthenticated("Invalid or expired token.") from exc

    claims = ClerkClaims(sub=decoded["sub"], email=decoded.get("email"))
    _claims_cache[token] = claims
    return claims

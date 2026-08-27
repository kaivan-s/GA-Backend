"""@require_auth decorator: verifies Clerk JWT and JIT-provisions the app user."""
from __future__ import annotations

from functools import wraps

from flask import g, request

from app.core.auth.clerk import verify_clerk_jwt
from app.errors import Unauthenticated


def _bearer_token() -> str:
    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        raise Unauthenticated("Missing bearer token.")
    return header.split(" ", 1)[1].strip()


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Imported lazily to avoid a circular import with the users domain.
        from app.domains.users.service import UserService

        claims = verify_clerk_jwt(_bearer_token())
        g.current_user = UserService().provision(claims)
        return fn(*args, **kwargs)

    return wrapper


def current_user():
    user = getattr(g, "current_user", None)
    if user is None:
        raise Unauthenticated("No authenticated user in context.")
    return user

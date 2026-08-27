"""Typed exceptions + a single JSON error envelope handler."""
from __future__ import annotations

from flask import Flask, g, jsonify
from werkzeug.exceptions import HTTPException


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str | None = None, *, code: str | None = None):
        super().__init__(message or self.code)
        self.message = message or self.__class__.__name__
        if code:
            self.code = code


class ValidationError(AppError):
    status_code = 400
    code = "validation_error"


class Unauthenticated(AppError):
    status_code = 401
    code = "unauthenticated"


class UpgradeRequired(AppError):
    status_code = 402
    code = "upgrade_required"


class Forbidden(AppError):
    status_code = 403
    code = "forbidden"


class NotFound(AppError):
    status_code = 404
    code = "not_found"


class Conflict(AppError):
    status_code = 409
    code = "conflict"


class RateLimited(AppError):
    status_code = 429
    code = "rate_limited"


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def _handle_app_error(err: AppError):
        payload = {
            "error": {
                "code": err.code,
                "message": err.message,
                "request_id": getattr(g, "request_id", None),
            }
        }
        return jsonify(payload), err.status_code

    @app.errorhandler(HTTPException)
    def _handle_http_exception(err: HTTPException):
        # Normal HTTP outcomes (404, 405, 400, ...) are client errors, not crashes.
        # Return the correct status without logging a traceback.
        status = err.code or 500
        payload = {
            "error": {
                "code": (err.name or "http_error").lower().replace(" ", "_"),
                "message": err.description or err.name,
                "request_id": getattr(g, "request_id", None),
            }
        }
        # Server-side HTTP errors (5xx) are worth logging; client errors (4xx) are not.
        if status >= 500:
            app.logger.exception("http_server_error", exc_info=err)
        return jsonify(payload), status

    @app.errorhandler(Exception)
    def _handle_unexpected(err: Exception):
        payload = {
            "error": {
                "code": "internal_error",
                "message": "Something went wrong.",
                "request_id": getattr(g, "request_id", None),
            }
        }
        app.logger.exception("unhandled_exception", exc_info=err)
        return jsonify(payload), 500

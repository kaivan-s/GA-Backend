"""Structured logging + per-request id."""
from __future__ import annotations

import logging
import uuid

from flask import Flask, g, request


def configure_logging(app: Flask) -> None:
    level = app.config.get("SETTINGS").log_level
    logging.basicConfig(
        level=level,
        format='{"level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
    )

    @app.before_request
    def _assign_request_id() -> None:
        g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))

    @app.after_request
    def _echo_request_id(response):
        if getattr(g, "request_id", None):
            response.headers["X-Request-Id"] = g.request_id
        return response

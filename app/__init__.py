"""Flask application factory."""
from __future__ import annotations

from flask import Flask, jsonify

from app.config import get_settings
from app.core.supabase_client import SupabaseClient
from app.errors import register_error_handlers
from app.extensions import set_supabase
from app.logging import configure_logging


def create_app() -> Flask:
    app = Flask(__name__)
    settings = get_settings()
    app.config["SETTINGS"] = settings

    set_supabase(SupabaseClient(settings))
    configure_logging(app)
    register_error_handlers(app)
    _register_blueprints(app)

    @app.get("/")
    def root():
        return jsonify({"service": "gratitude-backend", "status": "ok"})

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    @app.get("/readyz")
    def readyz():
        return jsonify({"status": "ready"})

    return app


def _register_blueprints(app: Flask) -> None:
    from app.domains.achievements.routes import bp as achievements_bp
    from app.domains.billing.routes import bp as billing_bp
    from app.domains.content.routes import bp as content_bp
    from app.domains.custom_prompts.routes import bp as custom_prompts_bp
    from app.domains.programs.routes import bp as programs_bp
    from app.domains.progress.routes import bp as progress_bp
    from app.domains.reminders.routes import bp as reminders_bp
    from app.domains.ritual.routes import bp as ritual_bp
    from app.domains.users.routes import bp as users_bp
    from app.domains.users.webhooks import bp as user_webhooks_bp
    from app.domains.values.routes import bp as values_bp

    for bp in (
        users_bp,
        user_webhooks_bp,
        content_bp,
        ritual_bp,
        progress_bp,
        billing_bp,
        reminders_bp,
        custom_prompts_bp,
        achievements_bp,
        values_bp,
        programs_bp,
    ):
        app.register_blueprint(bp)

"""12-factor settings. Fails fast when required env vars are missing in production."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    flask_env: str = "development"
    log_level: str = "INFO"

    # Supabase (new API key format: publishable + secret)
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_secret_key: str = ""
    supabase_jwks_url: str = ""
    supabase_db_url: str = ""
    media_url_ttl_seconds: int = 3600

    # Clerk
    clerk_publishable_key: str = ""
    clerk_issuer: str = ""
    clerk_jwks_url: str = ""
    clerk_audience: str = ""
    clerk_webhook_secret: str = ""

    # Apple
    apple_bundle_id: str = ""
    apple_issuer_id: str = ""
    apple_key_id: str = ""
    apple_private_key: str = ""
    apple_assn_env: str = "sandbox"

    # APNs
    apns_key_id: str = ""
    apns_team_id: str = ""
    apns_auth_key: str = ""
    apns_topic: str = ""

    # Ritual / day logic
    evening_cutoff_hour: int = 17
    default_day_reset_hour: int = 3

    @property
    def is_production(self) -> bool:
        return self.flask_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()

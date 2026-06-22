from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = "Bulgaria Property Alert"
    app_base_url: str = "http://127.0.0.1:8000"
    app_timezone: str = "Europe/Sofia"
    database_url: str = "sqlite:///./var/bulgaria-property-alert.db"
    listing_provider: str = "fixture"
    imot_live_enabled: bool = False
    fixture_html_path: str = "tests/fixtures/imot_search_sample.html"
    email_backend: str = "smtp"
    email_preview_dir: str = "var/email-previews"
    email_from: str = "alerts@example.com"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_starttls: bool = True
    scheduler_enabled: bool = False
    scheduler_mode: str = "interval"
    scheduler_interval_minutes: int = 60
    daily_run_time: str = "08:00"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8-sig",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

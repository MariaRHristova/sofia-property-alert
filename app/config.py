import os
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _is_truthy(value: str | None) -> bool:
    return value not in {None, '', '0', 'false', 'False'}


class Settings(BaseSettings):
    app_title: str = 'Sofia Property Alert'
    app_base_url: str = 'http://127.0.0.1:8000'
    app_timezone: str = 'Europe/Sofia'
    app_secure_cookies: bool = False
    database_url: str = 'sqlite:///./var/bulgaria-property-alert.db'
    listing_provider: str = 'fixture'
    imot_live_enabled: bool = False
    fixture_html_path: str = 'tests/fixtures/imot_search_sample.html'
    email_backend: str = 'smtp'
    email_preview_dir: str = 'var/email-previews'
    email_from: str = 'alerts@example.com'
    smtp_host: str = 'smtp.gmail.com'
    smtp_port: int = 587
    smtp_username: str = ''
    smtp_password: str = ''
    smtp_use_starttls: bool = True
    scheduler_enabled: bool = False
    scheduler_mode: str = 'interval'
    scheduler_interval_minutes: int = 60
    daily_run_time: str = '08:00'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8-sig',
        case_sensitive=False,
    )

    @model_validator(mode='after')
    def apply_runtime_overrides(self) -> 'Settings':
        if _is_truthy(os.getenv('VERCEL')) or os.getenv('VERCEL_URL'):
            if self.app_base_url == 'http://127.0.0.1:8000':
                vercel_url = os.getenv('VERCEL_URL')
                if vercel_url:
                    self.app_base_url = f'https://{vercel_url}'
            if self.database_url == 'sqlite:///./var/bulgaria-property-alert.db':
                self.database_url = 'sqlite:////tmp/bulgaria-property-alert.db'
            if self.email_preview_dir == 'var/email-previews':
                self.email_preview_dir = '/tmp/email-previews'
            if self.app_secure_cookies is False:
                self.app_secure_cookies = True
            if (
                self.email_backend == 'smtp'
                and not self.smtp_username
                and not self.smtp_password
            ):
                self.email_backend = 'preview'
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

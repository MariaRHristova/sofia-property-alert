from __future__ import annotations

from app.config import Settings

COMMON_ENV_KEYS = (
    'APP_BASE_URL',
    'APP_SECURE_COOKIES',
    'DATABASE_URL',
    'EMAIL_BACKEND',
    'EMAIL_PREVIEW_DIR',
    'VERCEL',
    'VERCEL_URL',
)


def test_settings_keep_local_defaults_outside_vercel(monkeypatch) -> None:
    for key in COMMON_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_base_url == 'http://127.0.0.1:8000'
    assert settings.database_url == 'sqlite:///./var/bulgaria-property-alert.db'
    assert settings.email_preview_dir == 'var/email-previews'
    assert settings.email_backend == 'smtp'
    assert settings.app_secure_cookies is False


def test_settings_use_vercel_safe_defaults(monkeypatch) -> None:
    for key in COMMON_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv('VERCEL', '1')
    monkeypatch.setenv('VERCEL_URL', 'sofia-property-alert.vercel.app')

    settings = Settings(_env_file=None)

    assert settings.app_base_url == 'https://sofia-property-alert.vercel.app'
    assert settings.database_url == 'sqlite:////tmp/bulgaria-property-alert.db'
    assert settings.email_preview_dir == '/tmp/email-previews'
    assert settings.email_backend == 'preview'
    assert settings.app_secure_cookies is True

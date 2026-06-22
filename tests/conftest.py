from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.main as main_module
from app.db import Base


@pytest.fixture(autouse=True)
def isolated_app_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    """Keep route tests away from the real database and SMTP configuration."""
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=test_engine)

    monkeypatch.setattr(main_module, "engine", test_engine)
    monkeypatch.setattr(main_module, "SessionLocal", test_session_local)
    monkeypatch.setattr(main_module.settings, "email_backend", "preview")
    monkeypatch.setattr(main_module.settings, "imot_live_enabled", False)
    monkeypatch.setattr(
        main_module.settings,
        "email_preview_dir",
        str(tmp_path / "email-previews"),
    )
    monkeypatch.setattr(main_module.settings, "smtp_password", "")

    yield

    test_engine.dispose()
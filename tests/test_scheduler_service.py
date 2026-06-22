from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.services.scheduler import AppScheduler


@dataclass
class FakeJob:
    next_run_time: datetime | None


class FakeScheduler:
    def __init__(self) -> None:
        self.jobs: dict[str, FakeJob] = {}
        self.started = False
        self.shutdown_called = False

    def start(self) -> None:
        self.started = True

    def shutdown(self, wait: bool = False) -> None:
        self.shutdown_called = True

    def remove_all_jobs(self) -> None:
        self.jobs.clear()

    def add_job(
        self,
        func,
        trigger,
        id: str,
        max_instances: int,
        replace_existing: bool,
        coalesce: bool,
    ) -> None:
        self.jobs[id] = FakeJob(next_run_time=datetime(2026, 6, 22, 8, 0, 0))

    def get_job(self, job_id: str) -> FakeJob | None:
        return self.jobs.get(job_id)


class DummySettings:
    app_timezone = "Europe/Sofia"
    scheduler_enabled = False
    scheduler_mode = "interval"
    scheduler_interval_minutes = 60
    daily_run_time = "08:00"


class DummyConfig:
    def __init__(
        self,
        enabled: bool,
        mode: str,
        interval_minutes: int,
        daily_run_time: str,
    ) -> None:
        self.enabled = enabled
        self.mode = mode
        self.interval_minutes = interval_minutes
        self.daily_run_time = daily_run_time


class DummySession:
    def __init__(self, config: DummyConfig) -> None:
        self.config = config

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def get(self, model, key):
        return self.config


class DummySessionFactory:
    def __init__(self, config: DummyConfig) -> None:
        self.config = config

    def __call__(self):
        return DummySession(self.config)


def test_scheduler_starts_only_when_enabled() -> None:
    fake_scheduler = FakeScheduler()
    config = DummyConfig(False, "interval", 30, "08:00")
    manager = AppScheduler(
        session_factory_getter=lambda: DummySessionFactory(config),
        settings_getter=lambda: DummySettings(),
        job_runner=lambda: None,
        scheduler_factory=lambda: fake_scheduler,
    )

    manager.start()

    assert fake_scheduler.started is True
    assert fake_scheduler.get_job("listing_job") is None


def test_scheduler_blocks_overlapping_runs() -> None:
    fake_scheduler = FakeScheduler()
    config = DummyConfig(True, "interval", 30, "08:00")
    run_count = {"count": 0}

    def runner():
        run_count["count"] += 1
        return {"ok": True}

    manager = AppScheduler(
        session_factory_getter=lambda: DummySessionFactory(config),
        settings_getter=lambda: DummySettings(),
        job_runner=runner,
        scheduler_factory=lambda: fake_scheduler,
    )

    manager.start()
    manager._lock.acquire()
    try:
        acquired, result = manager.run_manual_job()
    finally:
        manager._lock.release()

    second_acquired, second_result = manager.run_manual_job()

    assert acquired is False
    assert result is None
    assert second_acquired is True
    assert second_result == {"ok": True}
    assert run_count["count"] == 1

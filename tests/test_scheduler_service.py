# ruff: noqa: E501
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
        args,
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
        user_id: int,
        enabled: bool,
        mode: str,
        interval_minutes: int,
        daily_run_time: str,
    ) -> None:
        self.user_id = user_id
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


class DummySessionFactory:
    def __init__(self, config: DummyConfig) -> None:
        self.config = config

    def __call__(self):
        return DummySession(self.config)


class DummySchedulerManager(AppScheduler):
    def _load_enabled_snapshots(self):
        return [self._load_snapshot(user_id=42)] if self._load_snapshot(user_id=42).enabled else []

    def _load_snapshot(self, *, user_id: int):
        config = self._session_factory_getter()().config
        return type("Snapshot", (), {
            "user_id": config.user_id,
            "enabled": config.enabled,
            "mode": config.mode,
            "interval_minutes": config.interval_minutes,
            "daily_run_time": config.daily_run_time,
        })()


def test_scheduler_starts_only_when_enabled() -> None:
    fake_scheduler = FakeScheduler()
    config = DummyConfig(42, False, "interval", 30, "08:00")
    manager = DummySchedulerManager(
        session_factory_getter=lambda: DummySessionFactory(config),
        settings_getter=lambda: DummySettings(),
        job_runner=lambda user_id: None,
        scheduler_factory=lambda: fake_scheduler,
    )

    manager.start()

    assert fake_scheduler.started is True
    assert fake_scheduler.get_job("listing_job_42") is None


def test_scheduler_blocks_overlapping_runs_per_user() -> None:
    fake_scheduler = FakeScheduler()
    config = DummyConfig(42, True, "interval", 30, "08:00")
    run_count = {"count": 0}

    def runner(user_id: int):
        run_count["count"] += 1
        return {"ok": True, "user_id": user_id}

    manager = DummySchedulerManager(
        session_factory_getter=lambda: DummySessionFactory(config),
        settings_getter=lambda: DummySettings(),
        job_runner=runner,
        scheduler_factory=lambda: fake_scheduler,
    )

    manager.start()
    manager._acquire_user(42)
    try:
        acquired, result = manager.run_manual_job(user_id=42)
    finally:
        manager._release_user(42)

    second_acquired, second_result = manager.run_manual_job(user_id=42)

    assert acquired is False
    assert result is None
    assert second_acquired is True
    assert second_result == {"ok": True, "user_id": 42}
    assert run_count["count"] == 1



# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.models import SchedulerConfig
from app.schemas import SchedulerConfigUpdate, SchedulerConfigView


@dataclass(slots=True)
class SchedulerSnapshot:
    user_id: int
    enabled: bool
    mode: str
    interval_minutes: int
    daily_run_time: str


class SchedulerConfigService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    def get_or_create(self, *, user_id: int) -> SchedulerConfig:
        config = self.session.scalar(
            select(SchedulerConfig).where(SchedulerConfig.user_id == user_id)
        )
        if config is not None:
            return config
        config = SchedulerConfig(
            user_id=user_id,
            enabled=self.settings.scheduler_enabled,
            mode=self.settings.scheduler_mode,
            interval_minutes=self.settings.scheduler_interval_minutes,
            daily_run_time=self.settings.daily_run_time,
        )
        self.session.add(config)
        self.session.commit()
        self.session.refresh(config)
        return config

    def update(self, *, user_id: int, payload: SchedulerConfigUpdate) -> SchedulerConfig:
        config = self.get_or_create(user_id=user_id)
        config.enabled = payload.enabled
        config.mode = payload.mode
        config.interval_minutes = payload.interval_minutes
        config.daily_run_time = payload.daily_run_time
        self.session.commit()
        self.session.refresh(config)
        return config

    def list_enabled(self) -> list[SchedulerConfig]:
        statement = select(SchedulerConfig).where(
            SchedulerConfig.enabled.is_(True),
            SchedulerConfig.user_id.is_not(None),
        )
        return list(self.session.scalars(statement))

    @staticmethod
    def snapshot(config: SchedulerConfig) -> SchedulerSnapshot:
        if config.user_id is None:
            raise ValueError("Scheduler config must belong to a user.")
        return SchedulerSnapshot(
            user_id=config.user_id,
            enabled=config.enabled,
            mode=config.mode,
            interval_minutes=config.interval_minutes,
            daily_run_time=config.daily_run_time,
        )


class AppScheduler:
    def __init__(
        self,
        session_factory_getter: Callable[[], sessionmaker],
        settings_getter: Callable[[], Settings],
        job_runner: Callable[[int], object],
        scheduler_factory: Callable[[], BackgroundScheduler] | None = None,
    ) -> None:
        self._session_factory_getter = session_factory_getter
        self._settings_getter = settings_getter
        self._job_runner = job_runner
        self._scheduler_factory = scheduler_factory or BackgroundScheduler
        self._scheduler: BackgroundScheduler | None = None
        self._state_lock = Lock()
        self._running_users: set[int] = set()
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._scheduler = self._scheduler_factory()
        self._scheduler.start()
        self._started = True
        self.sync_schedule()

    def shutdown(self) -> None:
        if self._scheduler is not None:
            self._scheduler.shutdown(wait=False)
        self._scheduler = None
        self._started = False
        with self._state_lock:
            self._running_users.clear()

    def sync_schedule(self) -> None:
        if self._scheduler is None:
            return
        self._scheduler.remove_all_jobs()
        for snapshot in self._load_enabled_snapshots():
            self._scheduler.add_job(
                self.run_scheduled_job,
                trigger=self._build_trigger(snapshot),
                args=[snapshot.user_id],
                id=self._job_id(snapshot.user_id),
                max_instances=1,
                replace_existing=True,
                coalesce=True,
            )

    def run_manual_job(self, *, user_id: int) -> tuple[bool, object | None]:
        if not self._acquire_user(user_id):
            return False, None
        try:
            return True, self._job_runner(user_id)
        finally:
            self._release_user(user_id)

    def run_scheduled_job(self, user_id: int) -> object | None:
        if not self._acquire_user(user_id):
            return None
        try:
            return self._job_runner(user_id)
        finally:
            self._release_user(user_id)

    def current_view(self, *, user_id: int) -> SchedulerConfigView:
        config = self._load_snapshot(user_id=user_id)
        next_run_at = None
        if self._scheduler is not None:
            job = self._scheduler.get_job(self._job_id(user_id))
            if job is not None and job.next_run_time is not None:
                next_run_at = job.next_run_time.isoformat()
        return SchedulerConfigView(
            enabled=config.enabled,
            mode=config.mode,
            interval_minutes=config.interval_minutes,
            daily_run_time=config.daily_run_time,
            next_run_at=next_run_at,
            running=self._is_running(user_id),
        )

    def _load_enabled_snapshots(self) -> list[SchedulerSnapshot]:
        session_factory = self._session_factory_getter()
        settings = self._settings_getter()
        with session_factory() as session:
            service = SchedulerConfigService(session, settings)
            return [service.snapshot(item) for item in service.list_enabled()]

    def _load_snapshot(self, *, user_id: int) -> SchedulerSnapshot:
        session_factory = self._session_factory_getter()
        settings = self._settings_getter()
        with session_factory() as session:
            service = SchedulerConfigService(session, settings)
            config = service.get_or_create(user_id=user_id)
            return service.snapshot(config)

    def _build_trigger(
        self,
        config: SchedulerSnapshot,
    ) -> IntervalTrigger | CronTrigger:
        if config.mode == "daily_time":
            hours, minutes = config.daily_run_time.split(":", maxsplit=1)
            return CronTrigger(
                hour=int(hours),
                minute=int(minutes),
                timezone=self._settings_getter().app_timezone,
            )
        return IntervalTrigger(
            minutes=config.interval_minutes,
            timezone=self._settings_getter().app_timezone,
        )

    def _job_id(self, user_id: int) -> str:
        return f"listing_job_{user_id}"

    def _acquire_user(self, user_id: int) -> bool:
        with self._state_lock:
            if user_id in self._running_users:
                return False
            self._running_users.add(user_id)
            return True

    def _release_user(self, user_id: int) -> None:
        with self._state_lock:
            self._running_users.discard(user_id)

    def _is_running(self, user_id: int) -> bool:
        with self._state_lock:
            return user_id in self._running_users


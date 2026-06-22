from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.models import SchedulerConfig
from app.schemas import SchedulerConfigUpdate, SchedulerConfigView


@dataclass(slots=True)
class SchedulerSnapshot:
    enabled: bool
    mode: str
    interval_minutes: int
    daily_run_time: str


class SchedulerConfigService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    def get_or_create(self) -> SchedulerConfig:
        config = self.session.get(SchedulerConfig, 1)
        if config is not None:
            return config
        config = SchedulerConfig(
            id=1,
            enabled=self.settings.scheduler_enabled,
            mode=self.settings.scheduler_mode,
            interval_minutes=self.settings.scheduler_interval_minutes,
            daily_run_time=self.settings.daily_run_time,
        )
        self.session.add(config)
        self.session.commit()
        self.session.refresh(config)
        return config

    def update(self, payload: SchedulerConfigUpdate) -> SchedulerConfig:
        config = self.get_or_create()
        config.enabled = payload.enabled
        config.mode = payload.mode
        config.interval_minutes = payload.interval_minutes
        config.daily_run_time = payload.daily_run_time
        self.session.commit()
        self.session.refresh(config)
        return config

    @staticmethod
    def snapshot(config: SchedulerConfig) -> SchedulerSnapshot:
        return SchedulerSnapshot(
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
        job_runner: Callable[[], object],
        scheduler_factory: Callable[[], BackgroundScheduler] | None = None,
    ) -> None:
        self._session_factory_getter = session_factory_getter
        self._settings_getter = settings_getter
        self._job_runner = job_runner
        self._scheduler_factory = scheduler_factory or BackgroundScheduler
        self._scheduler: BackgroundScheduler | None = None
        self._lock = Lock()
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

    def sync_schedule(self) -> None:
        if self._scheduler is None:
            return
        config = self._load_snapshot()
        self._scheduler.remove_all_jobs()
        if not config.enabled:
            return
        self._scheduler.add_job(
            self.run_scheduled_job,
            trigger=self._build_trigger(config),
            id="listing_job",
            max_instances=1,
            replace_existing=True,
            coalesce=True,
        )

    def run_manual_job(self) -> tuple[bool, object | None]:
        if not self._lock.acquire(blocking=False):
            return False, None
        try:
            return True, self._job_runner()
        finally:
            self._lock.release()

    def run_scheduled_job(self) -> object | None:
        if not self._lock.acquire(blocking=False):
            return None
        try:
            return self._job_runner()
        finally:
            self._lock.release()

    def current_view(self) -> SchedulerConfigView:
        config = self._load_snapshot()
        next_run_at = None
        if self._scheduler is not None:
            job = self._scheduler.get_job("listing_job")
            if job is not None and job.next_run_time is not None:
                next_run_at = job.next_run_time.isoformat()
        return SchedulerConfigView(
            enabled=config.enabled,
            mode=config.mode,
            interval_minutes=config.interval_minutes,
            daily_run_time=config.daily_run_time,
            next_run_at=next_run_at,
            running=self._lock.locked(),
        )

    def _load_snapshot(self) -> SchedulerSnapshot:
        session_factory = self._session_factory_getter()
        settings = self._settings_getter()
        with session_factory() as session:
            service = SchedulerConfigService(session, settings)
            config = service.get_or_create()
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

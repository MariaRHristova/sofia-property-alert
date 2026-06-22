from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import select

from app.catalog import CITY_OPTIONS, PROPERTY_TYPES, ROOM_OPTIONS, TRANSACTION_TYPES
from app.config import get_settings
from app.db import Base, SessionLocal, engine
from app.email import delivery as email_delivery
from app.models import Listing
from app.schemas import SchedulerConfigUpdate, SubscriptionCreate
from app.services import listings as listings_service
from app.services.jobs import JobService, execute_job_run
from app.services.listings import load_listings_for_subscription
from app.services.preview import PreviewResult, build_preview
from app.services.scheduler import AppScheduler, SchedulerConfigService
from app.services.subscriptions import SubscriptionService, to_subscription_view

EmailService = email_delivery.EmailService
load_listings_for_subscriptions = listings_service.load_listings_for_subscriptions

settings = get_settings()
templates = Jinja2Templates(directory="app/templates")

scheduler_manager = AppScheduler(
    session_factory_getter=lambda: SessionLocal,
    settings_getter=lambda: settings,
    job_runner=lambda: execute_job_run(SessionLocal, settings),
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    from app import models as app_models

    _ = app_models
    Path("var").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    scheduler_manager.start()
    try:
        yield
    finally:
        scheduler_manager.shutdown()


app = FastAPI(title=settings.app_title, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def load_subscription_state() -> tuple[list[PreviewResult], int]:
    with SessionLocal() as session:
        service = SubscriptionService(session)
        subscriptions = [
            to_subscription_view(item) for item in service.list_subscriptions()
        ]
        listings = list(session.scalars(select(Listing)))
    previews = [build_preview(subscription, listings) for subscription in subscriptions]
    return previews, len(listings)


def load_scheduler_config() -> dict[str, object]:
    with SessionLocal() as session:
        config_service = SchedulerConfigService(session, settings)
        config_service.get_or_create()
    return scheduler_manager.current_view().model_dump()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
    preview_groups, listing_count = load_subscription_state()
    context = {
        "app_name": settings.app_title,
        "city_options_json": json.dumps(CITY_OPTIONS),
        "listing_count": listing_count,
        "listing_mode_description": (
            "live imot.bg search"
            if settings.imot_live_enabled
            else "local fixture provider"
        ),
        "listing_mode_label": (
            "Live listings" if settings.imot_live_enabled else "Fixture listings"
        ),
        "preview_groups": preview_groups,
        "property_types": PROPERTY_TYPES,
        "request": request,
        "room_options": ROOM_OPTIONS,
        "scheduler_config": load_scheduler_config(),
        "transaction_types": TRANSACTION_TYPES,
    }
    return templates.TemplateResponse(request, "index.html", context)


@app.post("/subscriptions")
async def create_subscription(request: Request) -> JSONResponse:
    try:
        payload = SubscriptionCreate.model_validate(await request.json())
    except ValidationError as exc:
        return JSONResponse(
            status_code=422,
            content={"errors": jsonable_encoder(exc.errors())},
        )
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body."})

    with SessionLocal() as session:
        service = SubscriptionService(session)
        subscription = service.create_subscription(payload)
        subscription_view = to_subscription_view(subscription)
        preview = build_preview(
            subscription_view,
            load_listings_for_subscription(subscription_view, settings),
        )
        job_service = JobService(session)
        job_service.persist_subscription_preview(
            subscription.id,
            preview.matches,
        )
        response_data = {
            "active": subscription_view.active,
            "city": subscription_view.city,
            "districts": subscription_view.districts,
            "email": subscription_view.email,
            "id": subscription_view.id,
            "initialized": subscription_view.initialized,
            "preview_match_count": len(preview.matches),
            "unsubscribe_url": (
                f"/subscriptions/{subscription_view.unsubscribe_token}/unsubscribe"
            ),
        }

    return JSONResponse(
        status_code=201,
        content=response_data,
    )


@app.api_route("/subscriptions/{token}/unsubscribe", methods=["GET", "POST"])
def unsubscribe_subscription(token: str, request: Request):
    with SessionLocal() as session:
        service = SubscriptionService(session)
        success = service.delete_subscription(token)

    if not success:
        if request.method == "GET":
            return HTMLResponse(
                status_code=404,
                content=(
                    "<html><body style='font-family:Arial,sans-serif;padding:24px;'>"
                    "<h1>Subscription not found</h1>"
                    "<p>The alert may already have been removed.</p>"
                    "<a href='/'>Return to the app</a>"
                    "</body></html>"
                ),
            )
        return JSONResponse(
            status_code=404,
            content={"error": "Subscription not found."},
        )

    if request.method == "GET":
        return HTMLResponse(
            status_code=200,
            content=(
                "<html><body style='font-family:Arial,sans-serif;padding:24px;'>"
                "<h1>You are unsubscribed</h1>"
                "<p>The alert was removed from your saved alerts.</p>"
                "<a href='/'>Back to the dashboard</a>"
                "</body></html>"
            ),
        )
    return JSONResponse(status_code=200, content={"status": "unsubscribed"})


@app.post("/subscriptions/{token}/subscribe")
def subscribe_subscription(token: str) -> JSONResponse:
    with SessionLocal() as session:
        service = SubscriptionService(session)
        subscription = service.reactivate_subscription(token)
        if subscription is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Subscription not found."},
            )
        subscription_view = to_subscription_view(subscription)
        preview = build_preview(
            subscription_view,
            load_listings_for_subscription(subscription_view, settings),
        )
        job_service = JobService(session)
        job_service.persist_subscription_preview(
            subscription.id,
            preview.matches,
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "subscribed",
            "preview_match_count": len(preview.matches),
        },
    )


@app.delete("/subscriptions/{token}")
def delete_subscription(token: str) -> JSONResponse:
    with SessionLocal() as session:
        service = SubscriptionService(session)
        success = service.delete_subscription(token)

    if not success:
        return JSONResponse(
            status_code=404,
            content={"error": "Subscription not found."},
        )
    return JSONResponse(status_code=200, content={"status": "deleted"})


@app.get("/scheduler/settings")
def read_scheduler_settings() -> dict[str, object]:
    return load_scheduler_config()


@app.post("/scheduler/settings")
async def update_scheduler_settings(request: Request) -> JSONResponse:
    try:
        payload = SchedulerConfigUpdate.model_validate(await request.json())
    except ValidationError as exc:
        return JSONResponse(
            status_code=422,
            content={"errors": jsonable_encoder(exc.errors())},
        )

    with SessionLocal() as session:
        config_service = SchedulerConfigService(session, settings)
        config_service.update(payload)
    scheduler_manager.sync_schedule()
    return JSONResponse(status_code=200, content=load_scheduler_config())


@app.post("/jobs/run")
def run_job() -> JSONResponse:
    acquired, result = scheduler_manager.run_manual_job()
    if not acquired:
        return JSONResponse(
            status_code=409,
            content={"error": "A job is already running."},
        )
    if result is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Job run did not produce a result."},
        )

    return JSONResponse(
        status_code=200,
        content={
            "active_subscriptions": result.active_subscriptions,
            "email_backend": result.email_backend,
            "email_errors": result.email_errors,
            "emails_sent": result.emails_sent,
            "job_run_id": result.job_run.id,
            "listings_created": result.listings_created,
            "listings_seen": result.listings_seen,
            "matches_created": result.matches_created,
            "preview_paths": result.preview_paths,
            "provider": result.job_run.provider,
            "status": result.job_run.status,
        },
    )


@app.get("/jobs/recent")
def recent_jobs() -> dict[str, object]:
    with SessionLocal() as session:
        job_service = JobService(session)
        jobs = job_service.list_recent_job_runs()

    return {
        "jobs": [
            {
                "id": job.id,
                "provider": job.provider,
                "status": job.status,
                "listings_seen": job.listings_seen,
                "listings_created": job.listings_created,
                "matches_created": job.matches_created,
                "emails_sent": job.emails_sent,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            }
            for job in jobs
        ]
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

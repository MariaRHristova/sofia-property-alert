from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.catalog import CITY_OPTIONS, PROPERTY_TYPES, ROOM_OPTIONS, TRANSACTION_TYPES
from app.config import get_settings
from app.db import Base, SessionLocal, engine
from app.email.delivery import EmailService
from app.providers.base import ListingCandidate
from app.providers.fixtures import FixtureListingProvider
from app.schemas import SubscriptionCreate
from app.services.jobs import JobService
from app.services.preview import PreviewResult, build_preview
from app.services.subscriptions import SubscriptionService, to_subscription_view

settings = get_settings()
templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    from app import models as app_models

    _ = app_models
    Path("var").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_title, lifespan=lifespan)


def load_fixture_listings() -> list[ListingCandidate]:
    provider = FixtureListingProvider(settings.fixture_html_path)
    fixture_exists = Path(settings.fixture_html_path).exists()
    return provider.fetch() if fixture_exists else []


def load_subscription_previews() -> list[PreviewResult]:
    listings = load_fixture_listings()
    with SessionLocal() as session:
        service = SubscriptionService(session)
        subscriptions = [
            to_subscription_view(item) for item in service.list_subscriptions()
        ]
    return [build_preview(subscription, listings) for subscription in subscriptions]


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
    fixture_listings = load_fixture_listings()
    previews = load_subscription_previews()
    context = {
        "app_name": settings.app_title,
        "city_options_json": json.dumps(CITY_OPTIONS),
        "fixture_sample_count": len(fixture_listings),
        "preview_groups": previews,
        "property_types": PROPERTY_TYPES,
        "request": request,
        "room_options": ROOM_OPTIONS,
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
        preview = build_preview(subscription_view, load_fixture_listings())

    unsubscribe_url = f"/subscriptions/{subscription.unsubscribe_token}/unsubscribe"
    return JSONResponse(
        status_code=201,
        content={
            "active": subscription.active,
            "city": subscription.city,
            "districts": subscription_view.districts,
            "email": subscription.email,
            "id": subscription.id,
            "initialized": subscription.initialized,
            "preview_match_count": len(preview.matches),
            "unsubscribe_url": unsubscribe_url,
        },
    )


@app.post("/subscriptions/{token}/unsubscribe")
def unsubscribe_subscription(token: str) -> JSONResponse:
    with SessionLocal() as session:
        service = SubscriptionService(session)
        success = service.deactivate_subscription(token)

    if not success:
        return JSONResponse(
            status_code=404,
            content={"error": "Subscription not found."},
        )
    return JSONResponse(status_code=200, content={"status": "unsubscribed"})


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


@app.post("/jobs/run")
def run_job() -> JSONResponse:
    listings = load_fixture_listings()
    with SessionLocal() as session:
        job_service = JobService(session)
        email_service = EmailService(settings)
        result = job_service.run_daily_job("fixture", listings, email_service)

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

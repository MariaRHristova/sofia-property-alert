from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator
from urllib.parse import parse_qs, urlencode

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.engine import make_url

from app.catalog import CITY_OPTIONS, PROPERTY_TYPES, ROOM_OPTIONS, TRANSACTION_TYPES
from app.config import get_settings
from app.db import Base, SessionLocal, engine
from app.email import delivery as email_delivery
from app.migrations import ensure_schema
from app.models import Listing
from app.schemas import (
    LoginForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    RegisterForm,
    SchedulerConfigUpdate,
    SubscriptionCreate,
)
from app.services import listings as listings_service
from app.services.auth import (
    SESSION_COOKIE_NAME,
    AuthenticatedUser,
    AuthError,
    AuthService,
)
from app.services.jobs import JobService, execute_job_run
from app.services.listings import load_listings_for_subscription
from app.services.preview import PreviewResult, build_preview
from app.services.scheduler import AppScheduler, SchedulerConfigService
from app.services.subscriptions import SubscriptionService, to_subscription_view

EmailService = email_delivery.EmailService
load_listings_for_subscriptions = listings_service.load_listings_for_subscriptions

settings = get_settings()
APP_NAME = "Sofia Property Alert"
templates = Jinja2Templates(directory="app/templates")

scheduler_manager = AppScheduler(
    session_factory_getter=lambda: SessionLocal,
    settings_getter=lambda: settings,
    job_runner=lambda user_id: execute_job_run(
        SessionLocal,
        settings,
        user_id=user_id,
    ),
)


def _ensure_sqlite_parent_directory(database_url: str) -> None:
    if not database_url.startswith('sqlite'):
        return
    try:
        database = make_url(database_url).database
    except Exception:
        return
    if not database:
        return
    Path(database).expanduser().parent.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    from app import models as app_models

    _ = app_models
    _ensure_sqlite_parent_directory(settings.database_url)
    Base.metadata.create_all(bind=engine)
    ensure_schema(engine)
    Base.metadata.create_all(bind=engine)
    scheduler_manager.start()
    try:
        yield
    finally:
        scheduler_manager.shutdown()


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


def _redirect(path: str, **params: str) -> RedirectResponse:
    location = path
    if params:
        location = f"{path}?{urlencode(params)}"
    return RedirectResponse(location, status_code=303)


async def _read_urlencoded_form(request: Request) -> dict[str, str]:
    payload = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
    return {key: values[-1] for key, values in payload.items()}


def _set_session_cookie(response: Response, session_token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        httponly=True,
        secure=settings.app_secure_cookies,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


def get_current_user(request: Request) -> AuthenticatedUser | None:
    with SessionLocal() as session:
        auth_service = AuthService(session, settings)
        return auth_service.get_authenticated_user(
            request.cookies.get(SESSION_COOKIE_NAME)
        )


def require_authenticated_user(request: Request) -> AuthenticatedUser:
    user = get_current_user(request)
    if user is None:
        raise AuthError("Sign in to continue.")
    return user


def require_authenticated_api_user(request: Request) -> AuthenticatedUser:
    csrf_token = request.headers.get("X-CSRF-Token")
    with SessionLocal() as session:
        auth_service = AuthService(session, settings)
        return auth_service.require_csrf(
            request.cookies.get(SESSION_COOKIE_NAME),
            csrf_token,
        )


def load_subscription_state(*, user_id: int) -> tuple[list[PreviewResult], int]:
    with SessionLocal() as session:
        service = SubscriptionService(session)
        subscriptions = [
            to_subscription_view(item)
            for item in service.list_subscriptions(user_id=user_id)
        ]
        listings = list(session.scalars(select(Listing)))
    previews = [build_preview(subscription, listings) for subscription in subscriptions]
    return previews, len(listings)


def load_scheduler_config(*, user_id: int) -> dict[str, object]:
    with SessionLocal() as session:
        config_service = SchedulerConfigService(session, settings)
        config_service.get_or_create(user_id=user_id)
    return scheduler_manager.current_view(user_id=user_id).model_dump()


def load_recent_jobs(*, user_id: int) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        job_service = JobService(session)
        jobs = job_service.list_recent_job_runs(user_id=user_id)
    return [
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


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
    current_user = get_current_user(request)
    preview_groups: list[PreviewResult] = []
    listing_count = 0
    scheduler_config: dict[str, object] | None = None
    recent_jobs: list[dict[str, Any]] = []
    if current_user is not None:
        preview_groups, listing_count = load_subscription_state(user_id=current_user.id)
        scheduler_config = load_scheduler_config(user_id=current_user.id)
        recent_jobs = load_recent_jobs(user_id=current_user.id)

    context = {
        "app_name": APP_NAME,
        "city_options_json": json.dumps(CITY_OPTIONS),
        "current_user": current_user,
        "flash_error": request.query_params.get("error"),
        "flash_notice": request.query_params.get("notice"),
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
        "scheduler_config": scheduler_config,
        "transaction_types": TRANSACTION_TYPES,
        "recent_jobs": recent_jobs,
    }
    return templates.TemplateResponse(request, "index.html", context)


@app.post("/auth/register")
async def register(request: Request) -> Response:
    form_data = await _read_urlencoded_form(request)
    try:
        payload = RegisterForm.model_validate(form_data)
    except ValidationError as exc:
        return _redirect("/", error=exc.errors()[0]["msg"])

    with SessionLocal() as session:
        auth_service = AuthService(session, settings)
        try:
            result = auth_service.register_user(payload.email, payload.password)
        except AuthError as exc:
            return _redirect("/", error=str(exc))

    EmailService(settings).send_message(
        result.verification_message,
        preview_key=f"verify-{result.user.id}",
    )
    return _redirect("/", notice="Account created. Check your email to verify it.")


@app.post("/auth/login")
async def login(request: Request) -> Response:
    form_data = await _read_urlencoded_form(request)
    try:
        payload = LoginForm.model_validate(form_data)
    except ValidationError:
        return _redirect("/", error="Invalid email or password.")

    with SessionLocal() as session:
        auth_service = AuthService(session, settings)
        try:
            user = auth_service.authenticate_user(payload.email, payload.password)
            session_bundle = auth_service.create_session(user)
        except AuthError as exc:
            return _redirect("/", error=str(exc))

    response = _redirect("/", notice="Signed in successfully.")
    _set_session_cookie(response, session_bundle.token)
    return response


@app.post("/auth/logout")
async def logout(request: Request) -> Response:
    current_user = require_authenticated_user(request)
    form_data = await _read_urlencoded_form(request)
    csrf_token = str(form_data.get("csrf_token", ""))
    with SessionLocal() as session:
        auth_service = AuthService(session, settings)
        try:
            auth_service.require_csrf(
                request.cookies.get(SESSION_COOKIE_NAME),
                csrf_token,
            )
            auth_service.revoke_session(request.cookies.get(SESSION_COOKIE_NAME))
        except AuthError as exc:
            return _redirect("/", error=str(exc))
    response = _redirect("/", notice=f"Signed out from {current_user.email}.")
    _clear_session_cookie(response)
    return response


@app.get("/auth/verify")
def verify_email(token: str) -> Response:
    with SessionLocal() as session:
        auth_service = AuthService(session, settings)
        try:
            user = auth_service.verify_email_token(token)
        except AuthError as exc:
            return _redirect("/", error=str(exc))
    return _redirect("/", notice=f"{user.email} is verified. You can sign in now.")


@app.post("/auth/password/request")
async def request_password_reset(request: Request) -> Response:
    form_data = await _read_urlencoded_form(request)
    try:
        payload = PasswordResetRequestForm.model_validate(form_data)
    except ValidationError:
        return _redirect(
            "/",
            notice="If the address exists, a reset link is on its way.",
        )

    with SessionLocal() as session:
        auth_service = AuthService(session, settings)
        result = auth_service.create_password_reset(payload.email)

    if result is not None:
        EmailService(settings).send_message(
            result.reset_message,
            preview_key=f"reset-{payload.email}",
        )
    return _redirect(
        "/",
        notice="If the address exists, a reset link is on its way.",
    )


@app.get("/auth/password/reset", response_class=HTMLResponse)
def render_password_reset(request: Request, token: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "reset_password.html",
        {
            "app_name": APP_NAME,
            "request": request,
            "token": token,
        },
    )


@app.post("/auth/password/reset")
async def reset_password(request: Request) -> Response:
    form_data = await _read_urlencoded_form(request)
    try:
        payload = PasswordResetForm.model_validate(form_data)
    except ValidationError as exc:
        return _redirect("/", error=exc.errors()[0]["msg"])

    with SessionLocal() as session:
        auth_service = AuthService(session, settings)
        try:
            auth_service.reset_password(payload.token, payload.password)
        except AuthError as exc:
            return _redirect("/", error=str(exc))
    return _redirect("/", notice="Password updated. Sign in with your new password.")


@app.post("/subscriptions")
async def create_subscription(request: Request) -> JSONResponse:
    try:
        current_user = require_authenticated_api_user(request)
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})

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
        subscription = service.create_subscription(
            payload,
            user_id=current_user.id,
            email=current_user.email,
        )
        subscription_view = to_subscription_view(subscription)
        preview = build_preview(
            subscription_view,
            load_listings_for_subscription(subscription_view, settings),
        )
        job_service = JobService(session)
        job_service.persist_subscription_preview(subscription.id, preview.matches)
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

    return JSONResponse(status_code=201, content=response_data)


@app.api_route("/subscriptions/{token}/unsubscribe", methods=["GET", "POST"])
def unsubscribe_subscription(token: str, request: Request):
    current_user = get_current_user(request)
    with SessionLocal() as session:
        service = SubscriptionService(session)
        success = service.deactivate_subscription(
            token,
            user_id=current_user.id if current_user else None,
        )

    if not success:
        if request.method == "GET":
            return HTMLResponse(
                status_code=404,
                content=(
                    "<html><body style='font-family:Arial,sans-serif;padding:24px;'>"
                    "<h1>Subscription not found</h1>"
                    "<p>The alert may already have been deactivated or removed.</p>"
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
                "<p>The alert was deactivated. You can subscribe again "
                "from the dashboard.</p>"
                "<a href='/'>Back to the dashboard</a>"
                "</body></html>"
            ),
        )
    return JSONResponse(status_code=200, content={"status": "unsubscribed"})


@app.post("/subscriptions/{token}/subscribe")
def subscribe_subscription(token: str, request: Request) -> JSONResponse:
    try:
        current_user = require_authenticated_api_user(request)
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})

    with SessionLocal() as session:
        service = SubscriptionService(session)
        subscription = service.reactivate_subscription(token, user_id=current_user.id)
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
        job_service.persist_subscription_preview(subscription.id, preview.matches)

    return JSONResponse(
        status_code=200,
        content={
            "status": "subscribed",
            "preview_match_count": len(preview.matches),
        },
    )


@app.delete("/subscriptions/{token}")
def delete_subscription(token: str, request: Request) -> JSONResponse:
    try:
        current_user = require_authenticated_api_user(request)
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})

    with SessionLocal() as session:
        service = SubscriptionService(session)
        success = service.delete_subscription(token, user_id=current_user.id)

    if not success:
        return JSONResponse(
            status_code=404,
            content={"error": "Subscription not found."},
        )
    return JSONResponse(status_code=200, content={"status": "deleted"})


@app.get("/scheduler/settings")
def read_scheduler_settings(request: Request) -> JSONResponse:
    try:
        current_user = require_authenticated_user(request)
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})
    return JSONResponse(content=load_scheduler_config(user_id=current_user.id))


@app.post("/scheduler/settings")
async def update_scheduler_settings(request: Request) -> JSONResponse:
    try:
        current_user = require_authenticated_api_user(request)
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})

    try:
        payload = SchedulerConfigUpdate.model_validate(await request.json())
    except ValidationError as exc:
        return JSONResponse(
            status_code=422,
            content={"errors": jsonable_encoder(exc.errors())},
        )

    with SessionLocal() as session:
        config_service = SchedulerConfigService(session, settings)
        config_service.update(user_id=current_user.id, payload=payload)
    scheduler_manager.sync_schedule()
    return JSONResponse(
        status_code=200,
        content=load_scheduler_config(user_id=current_user.id),
    )


@app.post("/jobs/run")
def run_job(request: Request) -> JSONResponse:
    try:
        current_user = require_authenticated_api_user(request)
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})

    acquired, result = scheduler_manager.run_manual_job(user_id=current_user.id)
    if not acquired:
        return JSONResponse(
            status_code=409,
            content={"error": "A job is already running for your account."},
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
def recent_jobs(request: Request) -> JSONResponse:
    try:
        current_user = require_authenticated_user(request)
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})
    return JSONResponse(content={"jobs": load_recent_jobs(user_id=current_user.id)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

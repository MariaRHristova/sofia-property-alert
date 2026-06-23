# Sofia Property Alert

Sofia Property Alert is a FastAPI web application that lets a user define real-estate search criteria for Sofia and receive a daily digest of newly discovered matching listings from imot.bg.

The project is built as an exam-friendly MVP with a fixture-backed parsing flow for deterministic tests and a live `imot.bg` integration path behind configuration.

## What the app does

- Create a property-search subscription
- Filter by Sofia district, transaction type, property type, price, rooms, and minimum area
- Parse and normalize listings from `imot.bg`-style result pages
- Match new listings against saved subscriptions without resending duplicates
- Render email digests separately from delivery
- Run the daily job manually from the UI or automatically through the new app-level scheduler
- Keep local `.eml` previews for safe inspection during development and tests

## Current implementation

- FastAPI + Jinja2 UI for subscriptions and job controls
- SQLite + SQLAlchemy persistence for subscriptions, listings, matches, and job runs
- BeautifulSoup-based parser for saved fixtures and real imot.bg result structure
- Fixture-backed tests for deterministic validation
- SMTP delivery support with preview mode for local development
- Token-based unsubscribe and permanent delete flows

## Technology

Python, FastAPI, Jinja2, SQLAlchemy, SQLite, APScheduler, BeautifulSoup, lxml, Pytest, and httpx.

## Run locally

The repository includes a virtual environment already, so you can usually start with:

```bash
.\scripts\run_pytest_clean.ps1 -q
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

If you prefer a fresh install, use the project dependencies from `pyproject.toml` and the settings in `.env.example`. The test wrapper runs Pytest against temporary database and email-preview paths and deletes them after the run, so agent verification does not pollute local app data.
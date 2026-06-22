---
name: fullstack-feature
description: Coordinate full-stack Bulgaria Property Alert product features that require FastAPI/SQLAlchemy backend work plus Jinja2/Bootstrap UI work, including API contract planning, conditional subagent implementation, verification, integration review, and plans.md updates. Use for cross-layer features, not small backend-only, frontend-only, documentation-only, or simple one-file tasks.
---

# Full-stack feature workflow

## Establish scope

1. Read `AGENTS.md` and `plans.md` when present. Inspect `README.md`, `pyproject.toml`, relevant code, tests, and the current diff before choosing commands or delegating.
2. Classify the request as backend-only, frontend-only, or full-stack.
3. Avoid multi-agent work for small or simple tasks. Handle a narrow one-layer or one-file change directly unless the user explicitly requests delegation.
4. Preserve the MVP and ask before adding dependencies, destructive schema changes, live scraping, real SMTP/email, CI/deployment changes, or expanded scope.

## Use project agents conditionally

- For a substantial backend-only task, ask `backend_engineer` to inspect and implement only when delegation materially helps.
- For a substantial frontend-only task, ask `frontend_engineer` to inspect and implement only when delegation materially helps.
- For a true full-stack task:
  1. Ask `backend_engineer` to inspect the relevant files and propose the backend/API/data contract before editing. Require request/response or render/redirect behavior, validation, persistence effects, and failure cases.
  2. Ask `frontend_engineer` to inspect the relevant files and propose UI integration against that contract, including form encoding, success, validation-error, empty, loading, accessibility, and responsive states.
  3. Reconcile disagreements in the parent thread. Record one agreed contract before either layer implements. Do not let agents silently invent incompatible field names, routes, auth, or error behavior.
  4. Implement in small, contract-aligned steps. Parallelize only independent files after the contract is stable; otherwise sequence backend contract work before UI wiring.
  5. After implementation and verification, ask the read-only `integration_reviewer` to review the final diff. Fix only evidenced correctness, security, contract, regression, or coverage issues; ignore style-only preferences.

## Respect project boundaries

- Backend: `app/main.py` thin route handlers, `app/config.py` settings, `app/db.py` SQLAlchemy session/engine, `app/models.py` ORM models, and `app/providers/` provider protocol, fixture adapter, and parsing.
- Frontend: FastAPI page routes plus planned `app/templates/` Jinja2 templates and `app/static/` Bootstrap/static assets. These directories do not exist yet; create them only for real UI work.
- Tests: `tests/`, with saved provider HTML under `tests/fixtures/`. Never make unit tests depend on live imot.bg.
- Planning/evidence: `plans.md` is the execution plan. Follow `AGENTS.md` for evidence rules during product implementation.
- Architecture: no account auth exists; the agreed MVP uses email subscriptions and tokenized unsubscribe. API routes are currently JSON REST-style. Keep provider normalization, database uniqueness/idempotency, UTC persistence, safe configuration, and separate email rendering/delivery.

## Verify and finish

1. Run the smallest relevant tests while iterating: `.\.venv\Scripts\python -m pytest <relevant-test-path>`
2. Run the full suite: `.\.venv\Scripts\python -m pytest`
3. Run lint: `.\.venv\Scripts\python -m ruff check .`
4. For UI behavior, run `.\.venv\Scripts\uvicorn app.main:app --reload` and open the affected pages in the embedded browser at `http://127.0.0.1:8000` when relevant. Verify normal, validation-error, empty, and responsive states honestly. There is no configured browser automation suite, typecheck command, or separate build command.
5. Update `plans.md` when the feature completes or changes planned scope/status; make only a focused plan edit.
6. Summarize changed files, agreed contract changes, user-facing behavior, verification actually run with results, and remaining risks. Never claim an unrun check passed.

## Example prompts

- `Use $fullstack-feature to add the subscription creation flow across FastAPI, SQLAlchemy, and the Jinja2/Bootstrap form. Reconcile the contract before implementation.`
- `Use $fullstack-feature to add tokenized unsubscribe with a confirmation page and tests, using project subagents only where the cross-layer work benefits.`
- `Use $fullstack-feature to add validation feedback for property criteria while preserving the current REST and database contracts.`


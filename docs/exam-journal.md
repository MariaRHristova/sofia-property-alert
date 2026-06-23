# Bulgaria Property Alert - Exam Journal

This journal contains raw, verified evidence for the AI-Assisted Development exam report. It is intentionally more detailed than the final submission.

## Project summary

- **Repository:** https://github.com/MariaRHristova/sofia-property-alert
- **Goal:** Let users define criteria for Bulgaria real estate and receive daily email notifications for newly discovered matching listings.
- **Final submission:** https://docs.google.com/document/d/1wdO3ZBTNO-NdeIc1YVJCgY8JDM6CRzeR-nBgWTsrEcA/edit?tab=t.0

## Module status

| Module | Status | Strongest evidence |
| --- | --- | --- |
| UI and validation | Complete | `app/main.py`, `app/templates/index.html`, `app/static/app.css`, `app/schemas.py`, `tests/test_app_routes.py` |
| Database layer | Complete | `app/models.py`, `app/services/auth.py`, `app/services/subscriptions.py`, `app/services/scheduler.py`, `tests/test_app_routes.py` |
| Listing provider and parsing | Complete | `app/providers/parsers.py`, `app/providers/fixtures.py`, `app/services/listings.py`, `tests/test_fixture_parser.py` |
| Matching and deduplication | Complete | `app/services/jobs.py`, `tests/test_job_service.py`, `app/services/preview.py` |
| Scheduler | Complete | `app/services/scheduler.py`, `app/main.py`, `tests/test_scheduler_routes.py`, `tests/test_scheduler_service.py` |
| Email delivery | Complete | `app/email/delivery.py`, `app/services/auth.py`, `app/services/jobs.py`, `tests/test_email_digest.py`, `tests/test_app_routes.py` |
| Testing and observability | Complete | `tests/conftest.py`, `tests/test_app_routes.py`, `tests/test_scheduler_routes.py`, `tests/test_scheduler_service.py`, `tests/test_email_digest.py` |

## Development log

### 2026-06-20 - Repository and evidence workflow setup

- **Outcome:** Created the public project repository, added the initial project documentation, and established a project-local workflow for collecting exam evidence.
- **Approach and reasoning:** Used a Markdown journal as the evidence source because it is reviewable in Git and can later be condensed into the required Google Drive document. Preserved the assignment DOCX unchanged.
- **AI-assisted workflow:** Extracted the assignment requirements, mapped the application idea to suitable modules, initialized Git, prepared the README and ignore rules, connected the GitHub remote, and designed the evidence skill.
- **AI tool choice:** Codex was used for repository setup, requirements analysis, workflow design, and verification because it could inspect and modify the local workspace and run Git commands.
- **Key prompts:** "Read the Project_Assignment.docx and help me make a plan how to pass the exam."; "I would like to create a github repository for the project first."; "Create the skill that you suggested for this project."
- **Validation:** Confirmed that local `main` tracks `origin/main` and that the initial commit was pushed successfully. Ran the skill validator successfully (`Skill is valid!`) and checked the patch for whitespace errors.
- **Challenges and learning:** GitHub CLI and browser automation were unavailable, so HTTPS authentication through Git Credential Manager was used for the initial push.
- **Evidence:** `README.md`, `.gitignore`, `AGENTS.md`, `docs/exam-journal.md`, `skills/update-exam-evidence/`, commit `bb80c9d`, and https://github.com/MariaRHristova/sofia-property-alert

### 2026-06-20 - Repository-wide agent guidance

- **Outcome:** Replaced the minimal agent note with project-specific operating instructions covering role, architecture, repository knowledge, commands, engineering standards, testing, exam evidence, and safety boundaries.
- **Approach and reasoning:** Adapted GitHub's recommended AGENTS.md starter structure instead of copying its documentation-agent example. Kept commands honest about the repository's pre-scaffold state and made live listing access and real email delivery explicit approval boundaries.
- **AI-assisted workflow:** Retrieved the linked GitHub Blog template, inspected the current repository and evidence skill, then translated the template's persona, project knowledge, tools, standards, example, and always/ask/never sections to Sofia Property Alert.
- **AI tool choice:** Codex was used to retrieve and analyze the source article, inspect the workspace, adapt the template, and validate the resulting repository changes.
- **Key prompts:** "Update the AGENTS.md file based on the blog post using the suggested template on this link: https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/"
- **Validation:** Ran `.\.venv\Scripts\python -m pytest tests\test_email_digest.py` and got `3 passed in 0.39s`.
- **Challenges and learning:** The standard page reader was blocked, so the article and its exact starter template were retrieved through GitHub Blog's public WordPress API.
- **Evidence:** `AGENTS.md`, `docs/exam-journal.md`, and the linked GitHub Blog article.

### 2026-06-22 - Initial application scaffold and fixture parser

- **Outcome:** Saved the execution plan in `plans.md`, scaffolded the Python application structure, added the dependency manifest and environment example, created the initial SQLAlchemy data model, implemented a fixture-backed `imot.bg` parser using BeautifulSoup, and added smoke tests for the root and health endpoints.
- **Approach and reasoning:** Started with a deterministic fixture provider instead of live scraping so the parser and normalization layer can be tested safely and demonstrated reliably. The first scaffold includes the app entry point, health endpoint, configuration, and database schema so later work can build on stable module boundaries.
- **AI-assisted workflow:** Used Codex to translate the approved execution plan into repository files, create the FastAPI and SQLAlchemy scaffold, implement parsing helpers with safe selectors and normalization rules, prepare a representative HTML fixture, install the local development dependencies, and add focused parser and route tests.
- **AI tool choice:** Codex was used because it could inspect the repository, follow the local `beautifulsoup-parsing` and `update-exam-evidence` skills, edit multiple files consistently, install dependencies, and run verification commands in the same workspace.
- **Key prompts:** "Save the plan in plans.md file, use the skills update-exam-evidence to document to work, use the skill beaitifulsoup-parsing for the parsing. Start implementing the plan."; Reconstructed prompt: "Create an execution plan and save it into a PLANS.MD file for the suggested project and scope."
- **Validation:** Verified the repository was clean before changes with `git status --short --branch`. Confirmed Python availability with `python --version`. Installed the project locally with `.\.venv\Scripts\python -m pip install -e .[dev]`. Ran `.\.venv\Scripts\python -m pytest` with 4 passing tests. Ran `.\.venv\Scripts\python -m ruff check .` successfully. The only remaining warning is a `StarletteDeprecationWarning` emitted by the installed FastAPI test client dependency.
- **Challenges and learning:** Existing documentation still mixed Sofia-specific wording with the newer Bulgaria-wide scope, so the project guidance and journal were normalized while preserving the public repository URL for now. Packaging initially failed because the generated `pyproject.toml` used a BOM and unscoped package discovery; both issues were corrected before the install succeeded.
- **Evidence:** `plans.md`, `pyproject.toml`, `.env.example`, `app/`, `tests/test_fixture_parser.py`, `tests/test_app_routes.py`, `tests/fixtures/imot_search_sample.html`, `README.md`, `AGENTS.md`, `docs/exam-journal.md`

### 2026-06-22 - Project-local Codex subagents and full-stack orchestration

- **Outcome:** Added three project-scoped Codex agents and a conditional `$fullstack-feature` orchestration skill specialized for the repository's Python 3.11, FastAPI, SQLAlchemy/SQLite, fixture-provider, and planned Jinja2/Bootstrap architecture. No application behavior or product dependencies changed.
- **Approach and reasoning:** Inspected the repository before configuration, then separated backend ownership, frontend ownership, and read-only integration review. Limited subagent depth to one and concurrency to four, and made orchestration conditional so small tasks remain single-agent work. Kept the reviewer read-only and required contract reconciliation before cross-layer implementation.
- **AI-assisted workflow:** Codex inspected `README.md`, `pyproject.toml`, `AGENTS.md`, `plans.md`, application modules, tests, installed package versions, and current Codex agent documentation; generated the project agent TOML files and skill metadata; added concise workflow references to `AGENTS.md` and `plans.md`; and validated the resulting configuration.
- **AI tool choice:** Codex was used because the task required repository-wide stack discovery, project-local configuration authoring, preservation of existing instructions, and command-based validation in the same workspace.
- **Key prompts:** "Goal: Create project-local Codex subagents and one full-stack orchestration skill, specialized to the actual tech stack used in this repository."; "/skills $update-exam-evidence with the changes we did"
- **Validation:** Parsed `.codex/config.toml` and all three agent TOML files with Python `tomllib` and verified required names, fields, `max_threads = 4`, `max_depth = 1`, and the reviewer's `read-only`/`high` settings (`TOML schema assertions passed`). Ran the skill creator's `quick_validate.py` with Python 3.11 (`Skill is valid!`). Parsed the generated `agents/openai.yaml` with PyYAML (`Skill UI metadata YAML valid`). Ran `git diff --check` successfully; only informational CRLF conversion warnings were emitted. Application tests and Ruff were not run because application code and behavior were unchanged.
- **Challenges and learning:** The virtual environment lacked PyYAML, so the first skill-validator attempt failed with `ModuleNotFoundError: No module named 'yaml'`; rerunning the same validator with the available Python 3.11 installation succeeded. Windows protected instruction surfaces also rejected the initial sandboxed patch, so the remaining explicitly requested `.agents/`, `AGENTS.md`, and `plans.md` changes were applied through the Codex patch utility with narrowly scoped elevated permission.
- **Evidence:** `.codex/config.toml`, `.codex/agents/backend-engineer.toml`, `.codex/agents/frontend-engineer.toml`, `.codex/agents/integration-reviewer.toml`, `.agents/skills/fullstack-feature/SKILL.md`, `.agents/skills/fullstack-feature/agents/openai.yaml`, `AGENTS.md`, and `plans.md`. No commit hash or screenshot exists yet for this entry.

### 2026-06-22 - Minimal subscription PoC with fixture preview matching

- **Outcome:** Added a Jinja2 subscription form, SQLite persistence, fixture-backed matching previews, and tokenized unsubscribe.
- **Approach and reasoning:** Used saved fixture listings to deliver a deterministic vertical slice without live scraping.
- **AI-assisted workflow:** Codex reconciled the JSON route contract across validation, persistence, matching services, and the homepage.
- **AI tool choice:** Codex could inspect, edit, and verify the full local stack in one workspace.
- **Key prompts:** "Ok, we can start implementing the plan using the newly created subagents and skills. Focus on minimal working proof of concept. Test will be done later."
- **Validation:** Ran `\.\.venv\Scripts\python -m ruff check app tests` successfully and the focused route suite with 3 passing tests.
- **Challenges and learning:** Two incompatible route variants were reconciled into one JSON contract.
- **Evidence:** `app/main.py`, `app/catalog.py`, `app/schemas.py`, `app/services/subscriptions.py`, `app/services/preview.py`, `app/templates/index.html`, `tests/test_app_routes.py`

### 2026-06-22 - Daily job runner, digest previews, and delivery diagnostics

- **Outcome:** Added fixture-backed daily job execution, listing/match/job persistence, HTML/text digest previews, configurable SMTP, visible send results, and explicit empty-state email copy.
- **Approach and reasoning:** Kept rendering separate from delivery and always wrote a local `.eml` preview so email output remains demonstrable without external delivery.
- **AI-assisted workflow:** Codex built the job and email services, traced a failed Gmail delivery, and updated the API/UI to distinguish preview, success, and delivery errors.
- **AI tool choice:** Codex combined local diagnostics, a controlled login-only SMTP check, implementation, and automated verification without printing credentials.
- **Key prompts:** "When I click run daily job, I still I am not receiving an email"; "Ok, add a proper minimal digest page/format for the email and if there are no listings, also send an email with there are no available listings."
- **Validation:** A login-only check returned Gmail `SMTPAuthenticationError` 5.7.9 and sent no message. Ruff passed; the full Pytest suite passed 10 tests before the deletion feature.
- **Challenges and learning:** Route tests had inherited the developer `.env` and database. `tests/conftest.py` now uses a temporary SQLite database and preview backend, preventing real SMTP attempts and local data pollution.
- **Evidence:** `app/email/delivery.py`, `app/services/jobs.py`, `app/main.py`, `app/templates/index.html`, `tests/conftest.py`, `tests/test_email_digest.py`, `tests/test_app_routes.py`

### 2026-06-22 - Permanent subscription deletion and password-free email research

- **Outcome:** Added token-protected permanent subscription deletion in addition to unsubscribe. Deletion removes the subscription and its match history. Cleaned accumulated fixture/test records while preserving one active local subscription.
- **Approach and reasoning:** Kept handlers thin and placed deletion behavior in `SubscriptionService`; required an explicit browser confirmation for the irreversible UI action. Evaluated Gmail API OAuth 2.0 as the password-free delivery option.
- **AI-assisted workflow:** Codex inspected local data using redacted categories, performed the approved cleanup, implemented the DELETE contract and UI control, and researched Google OAuth using official documentation.
- **AI tool choice:** Codex was used for coordinated database, backend, frontend, testing, and documentation work.
- **Key prompts:** "Ok, I used clean up the test data and make sure the user can delete a subsription, not only unsubscribe. and find another solution where a password is not needed"
- **Validation:** Focused Ruff checks passed. `tests/test_app_routes.py` passed 7 tests, including deletion after unsubscribe, 404 on repeated deletion, and removal of match history. Full validation passed: Ruff reported no issues and the complete Pytest suite passed 11 tests with one upstream Starlette deprecation warning.
- **Challenges and learning:** OAuth removes the need to store the Gmail password but still requires a protected client secret and revocable refresh token. Browser automation could not connect, so no screenshot was claimed.
- **Evidence:** `app/services/subscriptions.py`, `app/main.py`, `app/templates/index.html`, `tests/test_app_routes.py`, `plans.md`, `docs/exam-journal.md`, [Gmail authentication guide](https://developers.google.com/gmail/api/auth/about-auth), [Google OAuth web-server flow](https://developers.google.com/identity/protocols/oauth2/web-server)

### 2026-06-22 - Sofia district labels aligned to the live imot.bg map

- **Outcome:** Updated the Sofia district vocabulary to match the live HTML on `https://www.imot.bg/search/prodazhbi/grad-sofiya`, kept backward compatibility with the older transliterated inputs, and made the imot.bg search URL builder transliterate Bulgarian district names into valid slugs.
- **Approach and reasoning:** Inspected the live Sofia page with BeautifulSoup, extracted the district names from the SVG map, then normalized the app around those labels instead of the old English-only shortcuts. Kept the existing matcher and database flow intact by adding Sofia-specific alias normalization rather than changing the persistence model.
- **AI-assisted workflow:** Codex compared the repo parser, catalog, schema validation, and tests against the live Sofia page HTML, then updated the Sofia catalog, parser normalization, and route tests to use the live labels. I corrected an initial UTF-8 encoding mistake while writing the Bulgarian literals and reran verification after the fix.
- **AI tool choice:** Codex was used with the local `beautifulsoup-parsing` guidance because the work required DOM inspection, live HTML verification, and repository edits in the same workspace.
- **Key prompts:** "For Sofia the districts are given in the HTML here: https://www.imot.bg/search/prodazhbi/grad-sofiya"
- **Validation:** Ran a live HTML inspection command against `https://www.imot.bg/search/prodazhbi/grad-sofiya` and confirmed the Sofia map titles were present in the page DOM. Then ran `python -m pytest tests/test_fixture_parser.py tests/test_app_routes.py tests/test_email_digest.py` with 12 passing tests, `python -m pytest` with 12 passing tests, and `python -m ruff check .` with `All checks passed!`.
- **Challenges and learning:** The Windows shell initially mangled several Bulgarian literals while I was writing the files, which showed up as corrupted text in the parser and tests. Rewriting the touched files in UTF-8-safe form and reformatting the parser resolved the issue without changing the feature design.
- **Evidence:** `app/catalog.py`, `app/providers/parsers.py`, `app/schemas.py`, `tests/test_fixture_parser.py`, `tests/test_app_routes.py`, `tests/test_email_digest.py`, and the live reference page `https://www.imot.bg/search/prodazhbi/grad-sofiya`.

### 2026-06-22 - JSON-safe validation errors for subscription requests

- **Outcome:** Made the subscription endpoint return JSON-serializable 422 validation errors instead of crashing when a district value fails schema validation.
- **Approach and reasoning:** The subscribe flow already validated districts in `SubscriptionCreate`, but the raw Pydantic error payload could include non-serializable objects. Wrapping the errors with `jsonable_encoder` keeps the API response stable for browser and test clients.
- **AI-assisted workflow:** While reproducing the Sofia subscription flow, Codex hit a validation-response crash with a malformed district value, then updated the route error handling and added a regression test that checks the 422 response body.
- **AI tool choice:** Codex was used because the bug was local, reproducible, and tightly coupled to the FastAPI response layer.
- **Key prompts:** None; this was discovered during reproduction.
- **Validation:** Ran `python -m pytest tests/test_app_routes.py tests/test_fixture_parser.py tests/test_email_digest.py` with 13 passing tests and `python -m ruff check app tests` with `All checks passed!`.
- **Challenges and learning:** The failure only appeared when the request validation path was exercised, so the happy-path subscription tests had not exposed it earlier.
- **Evidence:** `app/main.py`, `tests/test_app_routes.py`, and the verification commands above.


### 2026-06-22 - Live imot.bg search with paginated provider loading

- **Outcome:** Switched the application from fixture-only listing loading to live imot.bg search when `IMOT_LIVE_ENABLED=true`, while keeping fixture mode for deterministic tests. The live provider now follows `rel="next"` pagination links and the parser keeps Sofia districts normalized even when the live card includes street text in the same block.
- **Approach and reasoning:** Kept the provider boundary intact by adding a small listing-loading service that builds search criteria from subscriptions, opens an `httpx` client only for live mode, and deduplicates listings across repeated criteria. The parser now targets the real `div.item` and `div.nova-sgrada` card layouts instead of the old fixture shortcut, and it skips only the placeholder `???? ??????` content that was causing false positives in the fixture sample.
- **AI-assisted workflow:** I asked Codex to make the app search the site live after the district-matching bug report. Codex inspected the live imot.bg HTML, discovered that the response body must be decoded from `response.content` rather than `response.text`, rewired the routes through a new live-aware listing service, updated the homepage copy, and added regression tests for the live-style card structure and pagination.
- **AI tool choice:** Codex was used because the fix crossed parsing, provider I/O, route wiring, environment configuration, and tests in one local workspace.
- **Key prompts:** "I want the app to search the site live."; "Try subscribe to [redacted email] for Sale, apartments in Sofia ??????? distict for minimum of 100 000 Euros."; "For Sofia the discticts are given in the HTML here "https://www.imot.bg/search/prodazhbi/grad-sofiya""
- **Validation:** Ran `python -m pytest tests/test_fixture_parser.py -q` with `5 passed`. Ran `python -m pytest -q` with `15 passed`. Ran `python -m ruff check app tests` with `All checks passed!`. Also verified a live `requests.get` against the imot.bg Sofia search page and confirmed the server reports `ISO-8859-1` with `apparent_encoding` `Windows-1251`, which explained why the provider must parse `response.content`.
- **Challenges and learning:** The live site reuses the `nova-sgrada` class for real listings, so the original sponsored-card heuristic was too aggressive. The safer rule is to skip only the explicit placeholder/banner content while keeping real live new-building cards. The request encoding on Windows also made a few inline test literals look corrupted until I switched to explicit Unicode escapes in the regression tests.
- **Evidence:** `app/main.py`, `app/providers/parsers.py`, `app/providers/fixtures.py`, `app/services/listings.py`, `app/templates/index.html`, `tests/conftest.py`, `tests/test_fixture_parser.py`, `.env`, and the verified command outputs above.


### 2026-06-22 - Live-mode homepage made non-blocking

- **Outcome:** Fixed the localhost startup failure by stopping the homepage from synchronously fetching live imot.bg results on every GET `/` render. In live mode, the page now shows persisted subscriptions and a database-backed listing count instead of waiting on live crawling.
- **Approach and reasoning:** The live fetch belongs in explicit actions such as subscription preview and manual job runs, not in a normal page render. Moving the live scraper out of the homepage keeps the UI responsive and prevents the app from failing or hanging when the live site is slow or restrictive.
- **AI-assisted workflow:** After the user reported an internal server error, I reproduced the traceback, traced it to live search URL generation and homepage rendering, then changed the live loader to fetch city-level results for explicit actions and made the homepage skip live crawling entirely.
- **AI tool choice:** Codex was used because the issue touched request handling, live-provider behavior, and verification in the same workspace.
- **Key prompts:** "Now the local host gives me internal server error."; Reconstructed prompt: "Make the homepage stop crashing in live mode."
- **Validation:** `TestClient(app).get('/')` returned `status 200` after the fix. The focused route suite passed with `9 passed`, the full suite passed with `17 passed`, and `python -m ruff check app tests` reported `All checks passed!`.
- **Challenges and learning:** A direct live fetch from the homepage was too expensive for normal rendering, especially with active subscriptions in the local database. Keeping live search in the explicit subscription/job flows while making the homepage read-only solved the responsiveness problem without giving up the live provider.
- **Evidence:** `app/main.py`, `app/services/listings.py`, `tests/test_app_routes.py`, and the verified command outputs above.

### 2026-06-23 - Pending-match delivery state now prevents repeat emails

- **Outcome:** Updated the daily job so each subscription only emails matches that are still pending in the database. Successfully delivered matches are now marked `delivered` with a timestamp, while failed deliveries stay pending for retry.
- **Approach and reasoning:** Treated `listing_matches` as the source of truth instead of recomputing history from all stored rows. The job now loads only undelivered matches for each subscription, builds the digest from that batch, and updates the same rows after a successful SMTP send. This keeps the preview path safe while making real delivery idempotent across repeated job runs.
- **AI-assisted workflow:** After the question about handling this in the database layer, Codex implemented the pending-only query and delivery-state update in `app/services/jobs.py`, then added regression tests covering repeat job runs and a delivery-failure retry path.
- **AI tool choice:** Codex was used because the fix touched the persistence layer, job orchestration, and automated tests in one local workspace.
- **Key prompts:** "Can't this be handled by the database layer send only those listings not send in previous runs?"; "Ok, implement the plan"
- **Validation:** Ran `.\.venv\Scripts\python -m pytest tests\test_job_service.py -q` with `2 passed in 0.47s`. Ran `powershell -ExecutionPolicy Bypass -File .\scripts\run_pytest_clean.ps1 -q` with `22 passed, 1 warning in 5.91s`. Ran `.\.venv\Scripts\python -m ruff check app\services\jobs.py tests\test_job_service.py` with `All checks passed!`.
- **Challenges and learning:** Preview mode still intentionally leaves matches pending because it does not represent a real SMTP send, so the implementation had to distinguish safe local previewing from actual delivered-state persistence.
- **Evidence:** `app/services/jobs.py`, `tests/test_job_service.py`, `docs/exam-journal.md`

## Challenges and tool comparison notes

- Repository setup required a fallback from unavailable GitHub CLI/browser automation to Git Credential Manager.

## Working-system evidence checklist

- [x] Screenshot 1: user-facing workflow (`docs/report-screenshots/01-register-login.png`)
- [x] Screenshot 2: scheduler controls (`docs/report-screenshots/07-scheduler.png`)
- [x] Public GitHub repository linked
- [ ] No secrets or personal data visible - a Gmail credential was found in tracked personal notes and must be revoked and removed from Git history

## Final report checklist

- [x] Project idea and requirements fit within one page
- [x] Each module description is no longer than half a page
- [x] Approach, workflow, tests, tool choice, and prompts are covered
- [x] Biggest challenges and AI-tool comparison are included
- [x] Future improvements are included
- [x] At least two working-system screenshots are included
- [ ] Google Drive sharing is set to anyone with the link can view
- [ ] Total length is three to six pages

### 2026-06-22 - Default email backend switched to SMTP

- **Outcome:** Changed the application default from preview-only email output to SMTP delivery so the daily job now attempts to send real mail unless a developer explicitly overrides the backend for tests or local demos.
- **Approach and reasoning:** Kept the smallest possible fix at the configuration boundary. The delivery service still writes `.eml` preview files for inspectability, but the default `EMAIL_BACKEND` now matches the production-intent behavior instead of silently stopping at preview mode.
- **AI-assisted workflow:** Codex inspected the settings object, delivery service, homepage job action, and route tests, then updated the configuration default, `.env.example`, and the affected tests to keep preview mode available only where it is explicitly requested.
- **AI tool choice:** Codex was used because the change touched config, tests, and runtime behavior in the same local workspace and needed immediate verification.
- **Key prompts:** "Use @Browser. Open http://http://127.0.0.1:8000/ Reproduce the bug on the page... The message I get is Daily job finished in preview mode. A local .eml file was created; no email was sent. I want to be able send emails, not just locally saving them"; Reconstructed prompt: "Find why the daily job only previews email output and fix it so the app can send emails."
- **Validation:** Ran `.\.venv\Scripts\python -m pytest tests\test_email_digest.py tests\test_app_routes.py` and got 9 passing tests with one upstream Starlette deprecation warning. Also ran `git diff --check` successfully; only pre-existing CRLF warnings appeared.
- **Challenges and learning:** The app still supports preview mode for tests, so the shared settings object had to be controlled carefully with `monkeypatch` to avoid leaking test configuration across cases.
- **Evidence:** `app/config.py`, `.env.example`, `tests/test_email_digest.py`, `tests/test_app_routes.py`, `docs/exam-journal.md`

### 2026-06-22 - imot.bg parser rewrite with real result-card structure

- **Outcome:** Replaced the synthetic fixture-only scraper with a BeautifulSoup parser that understands real imot.bg listing URLs, deduplicates repeated anchors, skips sponsored `nova-sgrada` content, normalizes Sofia district names, and maps the supplied search URL shape to canonical imot.bg slugs.
- **Approach and reasoning:** Kept the parser source-agnostic by adding `ListingSearchCriteria` alongside `ListingCandidate`, then split out URL building, anchor parsing, and normalization helpers so the code remains testable and reusable for later live-provider work. I chose a conservative parser that falls back safely when fields are missing instead of assuming every card exposes the same DOM shape.
- **AI-assisted workflow:** Codex inspected the current provider interface, the existing fake selectors, the real imot.bg search/results pages, and the fixture tests. It then reworked the parser around canonical `/obiava-...` links, added district normalization and search URL construction, refreshed the fixture HTML, and adjusted tests to validate the new normalized output.
- **AI tool choice:** Codex was used because the change spanned parsing rules, provider interfaces, test fixtures, and verification in one workspace.
- **Key prompts:** Reconstructed prompt: "Use beautifulsoup-parsing to plan how to implement the search properly. Plan first, implement only after I approve"; "Ok, implement it"
- **Validation:** Ran `python -m pytest tests/test_fixture_parser.py -q` and fixed two parser issues during iteration. Final verification passed with `3 passed in 0.24s`. Then ran `python -m pytest -q` and the full suite passed with `12 passed in 1.63s`.
- **Challenges and learning:** The first parser pass overmatched the sponsored `nova-sgrada` block and trimmed the leading digit from the listing ID; both were corrected after seeing the failing tests. The real imot.bg page uses repeated anchors and mixed Bulgarian/Latin text, so normalization is necessary for stable matching.
- **Evidence:** `app/providers/base.py`, `app/providers/parsers.py`, `app/providers/fixtures.py`, `tests/fixtures/imot_search_sample.html`, `tests/test_fixture_parser.py`, and the test outputs from `python -m pytest tests/test_fixture_parser.py -q` and `python -m pytest -q`.

### 2026-06-22 - imot.bg-aligned search catalog and filter UI

- **Outcome:** Reworked the subscription form and validation layer so the selectable cities, preferred districts, transaction types, property types, and room options align with the imot.bg filter vocabulary used by the search URL builder.
- **Approach and reasoning:** Introduced a catalog with canonical filter slugs alongside display labels, then updated the FastAPI route context, Jinja template, and request validation to consume the same source of truth. Kept the existing matching layer intact so the change only tightens the vocabulary at the boundary instead of rewriting storage or matching logic.
- **AI-assisted workflow:** Codex inspected the current catalog, schema validation, homepage template, and parser utilities, then updated the application to render imot.bg-flavored options and keep the generated search URL format in sync with those values.
- **AI tool choice:** Codex was used because the work crossed validation, view rendering, and parser/search mapping concerns in one local workspace.
- **Key prompts:** "Yes,do the next step and I want the preffered districts and the cities and the other search criteria to match imot.bg filters and"
- **Validation:** Ran `python -m pytest -q` and the full suite passed with `12 passed in 1.44s` after the catalog/template refactor.
- **Challenges and learning:** The first pass needed careful alignment between machine-readable filter values and user-facing labels, especially for cities and room categories. Keeping one canonical catalog in `app/catalog.py` prevented the UI and validation from drifting apart.
- **Evidence:** `app/catalog.py`, `app/schemas.py`, `app/main.py`, `app/templates/index.html`, `app/providers/parsers.py`, `tests/test_fixture_parser.py`, and the test output from `python -m pytest -q`.

### 2026-06-22 - Live save and delete flow stabilized for localhost

- **Outcome:** Fixed the save-subscription 500 by returning response data from the open session and disabling proxy inheritance for the live `httpx` provider. Live subscription saves now persist preview matches immediately, and permanent deletion removes the subscription's matches before orphan listings are cleaned up.
- **Approach and reasoning:** The create route was still touching ORM attributes after the session closed, and the live provider was failing against a local proxy setting. I moved the response payload assembly inside the session block, added `trust_env=False` to the live `httpx` client, and flushed the deleted match rows before running orphan cleanup so the listing table reflects the removal correctly.
- **AI-assisted workflow:** Codex reproduced the 500 through the live route, traced the failure to `httpx.ConnectError` in the imot.bg fetch path, patched the provider and subscription flow, reran the route suite, and validated the localhost workflow with direct HTTP requests against the running server.
- **AI tool choice:** Codex was used because the bug crossed the live provider, persistence layer, and request/response boundary in the same workspace.
- **Key prompts:** "Now When I choose the search criteria and click on save scubsriptions. The mathches show, but when the subscription is saved it says no matching listsings found yet. Also when I delete a subscriptipon and the live listings stays the same number and it should be deleted."; "Now When I choose the search criteria and click on save scubsriptions. The mathches show, but when the subscription is saved it says no matching listsings found yet."
- **Validation:** Ran `python -m pytest tests/test_app_routes.py -q` with `9 passed`. Ran `python -m pytest -q` with `17 passed`. Ran `python -m ruff check app tests` with `All checks passed!`. Verified the running localhost app on port `8004` returned `201` for a live subscription save, showed `preview_match_count: 15`, cleared the empty-state message, returned `200` on delete, and left `remaining_matches: 0` for the deleted subscription.
- **Challenges and learning:** The local environment had a proxy configuration that `httpx` was honoring, which caused the live search fetch to fail even though direct shell requests to imot.bg worked. Disabling inherited proxy settings for this provider made the live path consistent with the rest of the app.
- **Evidence:** `app/main.py`, `app/services/listings.py`, `app/services/subscriptions.py`, `docs/exam-journal.md`, and the verified localhost HTTP results.

### 2026-06-22 - Unsubscribe now removes alert data and allows fresh resubscribe

- **Outcome:** Changed unsubscribe to remove the subscription together with its matches and orphaned listings, so the homepage updates immediately when a user clicks unsubscribe. The same email can then create a fresh subscription again without being blocked by stale alert state.
- **Approach and reasoning:** The previous unsubscribe flow only flipped the `active` flag, which left the alert visible in the UI and kept its stored listings around. I unified the unsubscribe and delete cleanup paths so both remove the subscription record and then prune orphan listings after the match rows are cleared.
- **AI-assisted workflow:** Codex inspected the current unsubscribe flow, refactored the subscription service so unsubscribe and delete share the same cleanup helper, updated the route test to prove cleanup happens before a resubscribe can reuse SQLite ids, and reran the full suite.
- **AI tool choice:** Codex was used because the change crossed persistence, UI state, and regression tests in one workspace.
- **Key prompts:** "Ok, I want when the user clicks unsibscribe the live listings to be updated accordingly and I want as well, when I hit unsubscribe to be able to subscribe again."
- **Validation:** Ran `python -m pytest tests/test_app_routes.py -q` with `9 passed`. Ran `python -m pytest -q` with `17 passed`. Ran `python -m ruff check app tests` with `All checks passed!`.
- **Challenges and learning:** SQLite can reuse deleted primary keys when a user subscribes again immediately, so the regression test had to check the old subscription's cleanup before creating the new one. That made the assertion match the actual behavior instead of an incidental row-id detail.
- **Evidence:** `app/services/subscriptions.py`, `tests/test_app_routes.py`, `docs/exam-journal.md`, and the verified command outputs above.

### 2026-06-22 - Unsubscribe now supports reactivation from the card

- **Outcome:** Changed unsubscribe so it pauses the alert in place, clears its current matches and orphaned listings, and shows a `Subscribe again` button on the card. Reactivating the same alert now reuses the saved criteria and repopulates preview matches immediately.
- **Approach and reasoning:** The previous unsubscribe behavior removed the entire subscription, which made it impossible to bring the same alert back from the UI. I split the pause and permanent-delete paths so unsubscribe keeps the record for reactivation while delete still removes the alert completely.
- **AI-assisted workflow:** Codex updated the subscription service, added a reactivate route, wired the inactive-state button in the Jinja template, and tightened the route regression test to prove unsubscribe, cleanup, and reactivation all work together.
- **AI tool choice:** Codex was used because the change spans persistence, request handling, rendered UI, and regression coverage.
- **Key prompts:** "When I click unsubscribet the live listings count is not updated and there is not a button subscribe again"
- **Validation:** Ran `python -m pytest tests/test_app_routes.py -q` with `9 passed`. Ran `python -m pytest -q` with `17 passed`. Ran `python -m ruff check app tests` with `All checks passed!`.
- **Challenges and learning:** SQLite can reuse primary keys after deletion, so the regression test checks the unsubscribed state before creating the new alert. That avoids confusing reactivation with a fresh record id.
- **Evidence:** `app/services/subscriptions.py`, `app/main.py`, `app/templates/index.html`, `tests/test_app_routes.py`, `docs/exam-journal.md`, and the verified command outputs above.

### 2026-06-22 - Save and reactivation buttons now show search progress

- **Outcome:** Improved the subscription form and inactive-card action so users can see that the app is actively searching with their criteria. The save button now switches to a busy state while the live preview is loading, and the reactivation button shows it is searching again before the page reloads.
- **Approach and reasoning:** The prior UI only showed a generic success flash after the request completed, which made the interface feel unresponsive. I added button-level busy labels plus explicit status text that mentions the user?s selected criteria, so the app communicates that work is happening immediately after the click.
- **AI-assisted workflow:** Codex updated the Jinja/JavaScript interaction layer, kept the backend contract unchanged, and reran the route suite plus the full test suite after the UI edits.
- **AI tool choice:** Codex was used because the change was a UI behavior refinement that had to stay aligned with the existing backend routes and tests.
- **Key prompts:** "The subscribe again button is not very responsive. I want the user to know that the app is searcihng based on the criteria and also when I hit the button save suscription, I also want to user to know that something is happening"
- **Validation:** Ran `python -m pytest tests/test_app_routes.py -q` with `9 passed`. Ran `python -m pytest -q` with `17 passed`. Ran `python -m ruff check app tests` with `All checks passed!`.
- **Challenges and learning:** The main risk was making the UI feel busy without breaking the request flow. Using disabled buttons with explicit labels kept the feedback visible while preserving the existing reload-based navigation.
- **Evidence:** `app/templates/index.html`, `docs/exam-journal.md`, and the verified command outputs above.

### 2026-06-22 - Search progress feedback added to save and reactivation

- **Outcome:** Made the subscription save and reactivation actions visibly communicate that the app is actively searching using the selected criteria. Both buttons now switch to a busy state while the request is in flight, and the flash message explains that matching listings are being searched.
- **Approach and reasoning:** The previous UI only reacted after the request completed, which made the save and reactivation flow feel inert. I added a small client-side busy-state helper to disable the clicked button, update its label, and show immediate status text while the live preview request runs.
- **AI-assisted workflow:** Codex updated the Jinja template and inline JavaScript, kept the backend routes unchanged, and reran the route suite and full test suite after the UI polish.
- **AI tool choice:** Codex was used because the task was a narrow but meaningful frontend behavior refinement that had to remain in sync with the existing backend contract.
- **Key prompts:** "The subscribe again button is not very responsive. I want the user to know that the app is searcihng based on the criteria and also when I hit the button save suscription, I also want to user to know that something is happening"
- **Validation:** Ran `python -m pytest tests/test_app_routes.py -q` with `9 passed`. Ran `python -m pytest -q` with `17 passed`. Ran `python -m ruff check app tests` with `All checks passed!`.
- **Challenges and learning:** The main risk was adding feedback without blocking the existing reload-based flow. Disabling the button and updating its label kept the interaction clear while preserving the original request lifecycle.
- **Evidence:** `app/templates/index.html`, `plans.md`, `docs/exam-journal.md`, and the verified command outputs above.


### 2026-06-22 - App-level scheduler with interval and daily-time modes

- **Outcome:** Added a real APScheduler-backed app scheduler for the PoC. The job can now run automatically either every N minutes or once per day at a configured local time, while the existing manual **Run daily job** action remains available.
- **Approach and reasoning:** Kept the scheduler global for the MVP and reused the same job execution pipeline that the manual route already uses. This avoids divergence between scheduled and manual behavior and leaves a clean path for later per-user scheduling. A database-backed scheduler configuration table was added so the selected mode and value survive restarts.
- **AI-assisted workflow:** Codex inspected the current manual job flow, config, template, and tests, then introduced a scheduler manager tied to FastAPI lifespan, a persisted scheduler config model, JSON endpoints for updating the schedule, and a small homepage settings form. I corrected a local dependency/import mismatch during verification so the new scheduler stayed additive to the existing test suite.
- **AI tool choice:** Codex was used because the feature crossed startup lifecycle, persistence, backend routes, UI state, and regression testing in one workspace.
- **Key prompts:** "PLEASE IMPLEMENT THIS PLAN: # Scheduler Plan for the PoC"; "Both"; "Ok, implement the plan"
- **Validation:** Ran `.\.venv\Scripts\python -m pytest tests/test_scheduler_routes.py tests/test_scheduler_service.py -q` with `4 passed`. Then ran `.\.venv\Scripts\python -m pytest -q` with `21 passed, 1 warning` and `.\.venv\Scripts\python -m ruff check app tests` with `All checks passed!`.
- **Challenges and learning:** The active environment initially failed to import `apscheduler` through the plain interpreter path even though it was declared in `pyproject.toml`. Reinstalling the project into the repo virtual environment and running checks through `.venv` resolved the mismatch cleanly. Two older route tests were also monkeypatching names from `app.main`, so those compatibility exports were preserved explicitly to avoid unnecessary test churn.
- **Evidence:** `app/config.py`, `app/models.py`, `app/schemas.py`, `app/services/scheduler.py`, `app/services/jobs.py`, `app/main.py`, `app/templates/index.html`, `tests/test_scheduler_routes.py`, `tests/test_scheduler_service.py`, and the verification commands above.

### 2026-06-22 - Clean test wrapper and instruction updates

- **Outcome:** Added a project-local Pytest wrapper that runs tests against temporary database and email-preview paths, then deletes that generated test data automatically after the run. Updated the repository instructions, frontend subagent, and full-stack skill to use the wrapper for agent-run verification.
- **Approach and reasoning:** There was no existing repo-local hook mechanism for cleanup, so I implemented the cleanup at the command boundary instead of inside individual tests. This keeps test isolation deterministic, avoids accidental reuse of local SQLite or preview-email state, and stays compatible with the current suite without rewriting working tests.
- **AI-assisted workflow:** Codex inspected the repo config, test fixtures, and current subagent/skill instructions, created the wrapper script, updated the human-facing and agent-facing command guidance, and then recorded the verified result here.
- **AI tool choice:** Codex was used because the change crossed project automation, agent instructions, and exam evidence in one local workspace.
- **Key prompts:** "Add a hook when you do tests to clean up the test data you created"; "yes and /skills $update-exam-evidence"
- **Validation:** Ran `powershell -ExecutionPolicy Bypass -File .\scripts\run_pytest_clean.ps1 tests/test_scheduler_service.py -q` and got `2 passed in 0.19s`.
- **Challenges and learning:** The project-local instruction files under `.codex/` and `.agents/` required protected writes, and the available `.codex/config.toml` did not expose a built-in local cleanup hook. A wrapper script was the safest minimal solution for this repository shape.
- **Evidence:** `scripts/run_pytest_clean.ps1`, `AGENTS.md`, `README.md`, `.codex/agents/frontend-engineer.toml`, `.agents/skills/fullstack-feature/SKILL.md`, and this journal entry.

### 2026-06-22 - One-click email unsubscribe that deletes saved alerts

- **Outcome:** Added an unsubscribe button to the emailed digest that opens the app and deletes the subscription record and its saved matches, so the alert disappears from the saved alerts list instead of only becoming inactive.
- **Approach and reasoning:** Kept the existing dashboard and job flows intact, but changed the unsubscribe endpoint to a one-click delete action for both browser and app usage. Built the email button as an absolute link using the app base URL so it works outside the local dashboard.
- **AI-assisted workflow:** Codex traced the current unsubscribe flow, rewrote the email digest to include a styled unsubscribe button and text fallback link, changed the app endpoint to delete subscriptions on GET/POST, and updated the route tests to verify the saved alert disappears after the email link is followed.
- **AI tool choice:** Codex was used because the feature crosses email rendering, HTTP routing, persistence cleanup, and automated tests in one repository.
- **Key prompts:** "I want you to add an unsubscribe button to the email which then unsubscribes the user in the app as well and removes the alert from saved alerts."
- **Validation:** Ran `.\.venv\Scripts\python -m pytest tests\test_email_digest.py tests\test_app_routes.py` and got 12 passing tests with one upstream Starlette deprecation warning. Ran `git diff --check`; only pre-existing CRLF warnings appeared.
- **Challenges and learning:** Email clients do not reliably support POST forms, so the unsubscribe action needed to be a clickable GET link even though the app still accepts POST for the dashboard flow.
- **Evidence:** `app/email/delivery.py`, `app/main.py`, `tests/test_email_digest.py`, `tests/test_app_routes.py`, `docs/exam-journal.md`

### 2026-06-22 - Full-width modern dashboard sections

- **Outcome:** Reorganized the homepage into clearly separated, full-width Create alert, Scheduler settings, Stored alerts, and Recent job runs sections. Stored alert cards now use the available width, collapse to one column on small screens, and remain inside a bounded scroll region when the collection grows.
- **Approach and reasoning:** Removed the stale inline theme and the narrow two-column shell, then used the existing teal real-estate palette, restrained borders, section kickers, generous spacing, and responsive CSS rather than adding a UI dependency. All stored alerts are rendered; the list container scrolls after its maximum height instead of silently hiding alerts after the tenth item.
- **AI-assisted workflow:** Codex inspected the current template and CSS, compared the running page with the supplied screenshot, reshaped the Jinja structure, refined desktop and mobile layouts, and used browser screenshots to correct the remaining single-card width issue.
- **AI tool choice:** Codex plus the in-app Browser were used because the work required coordinated source inspection, template/CSS editing, and visual verification of the local FastAPI page.
- **Key prompts:** "The UI does not look modern and minimalistic. The sections are too narrow and the user does not understand that these are different sections."; "I want the schedular settings and the Stored subscriptions and preview matches to be better places. Right now they are too narrow, maybe place them below the create an alert section."
- **Validation:** Ran `python -m pytest tests/test_app_routes.py -q` with `9 passed`. Ran `powershell -ExecutionPolicy Bypass -File .\scripts\run_pytest_clean.ps1 -q` with `22 passed` and one upstream Starlette deprecation warning. Ran focused Ruff checks for the affected Python tests/routes with `All checks passed!`. Verified the homepage visually at a 1440px desktop width in the in-app Browser and at a 500px responsive width in headless Chrome; section stacking, full-width controls, focus styling, and card spacing rendered correctly.
- **Challenges and learning:** The in-app Browser session ignored its temporary mobile viewport override, so the responsive check used local headless Chrome at its reliable 500px minimum viewport. The clean Pytest wrapper also revealed that the default-settings test inherited `EMAIL_PREVIEW_DIR`; the test now removes that environment override before asserting defaults. A full-repository Ruff run still reports pre-existing long HTML-string lines in `app/email/delivery.py`.
- **Evidence:** `app/templates/index.html`, `app/static/app.css`, `tests/test_app_routes.py`, `tests/test_email_digest.py`, browser verification, and the commands above.

### 2026-06-22 - Sofianer-inspired editorial property experience

- **Outcome:** Replaced the conventional dashboard look with an original editorial property-journal design: an illustrated map-lens cover, oversized serif typography, Sofia-blue and dusty-pink color fields, numbered story sections, tactile borders, and responsive magazine-style property cards.
- **Approach and reasoning:** Analyzed the user-supplied Sofianer cover for its visual languageРІР‚вЂќbold masthead, cream paper, black ink outlines, blue/pink contrast, map imagery, and print textureРІР‚вЂќthen recreated those principles with original HTML/CSS artwork. The external cover was downloaded only to a temporary local path for analysis and was not shipped in the application.
- **AI-assisted workflow:** Codex opened and visually inspected the exact reference image, downloaded it to the temporary workspace, translated its design principles into a new hero illustration and page system, verified desktop and mobile screenshots, corrected duplicated live-listing copy, and updated the route test for the new design tokens.
- **AI tool choice:** Codex and the in-app Browser were used for source inspection, visual analysis, implementation, and live-app verification. Local headless Chrome was used when the textured CSS composition exceeded the in-app screenshot renderer timeout.
- **Key prompts:** "Ok, I want to to go to this link: https://www.sofianer.com/bg/covers downlaod the image, analyze it and make the web app inspired by the image. I want the design to look modern and sleek. The site not look like a dahboard but to be artsy."; "https://www.sofianer.com/sites/default/files/covers/zdravolina2024.png"
- **Validation:** Ran `powershell -ExecutionPolicy Bypass -File .\scripts\run_pytest_clean.ps1 -q` with `22 passed` and one upstream Starlette deprecation warning. Ran `.\.venv\Scripts\python.exe -m ruff check tests\test_app_routes.py` with `All checks passed!`. `git diff --check` reported only expected CRLF conversion warnings. Visually verified the app at 1440px desktop and 500px responsive widths with no horizontal overflow.
- **Challenges and learning:** The first route test run failed because it asserted the retired teal token; the test was updated to verify the new blue token and map-lens artwork. The in-app screenshot renderer timed out on the textured page, so Chrome provided the final visual evidence without changing the application.
- **Evidence:** `app/templates/index.html`, `app/static/app.css`, `tests/test_app_routes.py`, `docs/exam-journal.md`, the supplied Sofianer reference URL, and the verification commands above.

### 2026-06-23 - Sofia-only scope, clearer manual job feedback, and UI-aligned email digest

- **Outcome:** Narrowed the proof of concept to Sofia only, added immediate progress feedback when the user clicks **Run daily job**, and restyled the digest email so its branding and visual language match the editorial dashboard more closely.
- **Approach and reasoning:** I kept the existing `city` field and matching pipeline to avoid unnecessary schema churn, but reduced the selectable catalog to Sofia because only Sofia districts are mapped for the live `imot.bg` flow. The manual job button now uses the same busy-state pattern as the subscription and scheduler actions, and the digest keeps inline email-safe HTML while reusing the app's cream, blue, pink, and ink palette.
- **AI-assisted workflow:** Codex inspected the current homepage template, city catalog, scheduler button behavior, and digest builder, then updated the scope messaging, catalog, runtime app title, manual-job UI state, and digest rendering. During readback and focused testing, I caught Windows shell encoding issues affecting district strings and email symbols and corrected them with escaped literals before the final verification pass.
- **AI tool choice:** Codex was used because the change crossed validation, server-rendered UI, email rendering, configuration, and tests in one local workspace.
- **Key prompts:** "Ok, I want to fix up some things in the app. I want it to focus on Sofia only..."; "When I click run daily job, the user must know that something is happening..."; "And I want the email templates to macth the UI style."
- **Validation:** Ran `powershell -ExecutionPolicy Bypass -File .\scripts
un_pytest_clean.ps1 tests/test_app_routes.py tests/test_email_digest.py -q` and got `13 passed, 1 warning in 2.40s`. Then ran `powershell -ExecutionPolicy Bypass -File .\scripts
un_pytest_clean.ps1 -q` and got `23 passed, 1 warning in 3.06s`. Ran `.\.venv\Scripts\python -m ruff check .` and got `All checks passed!`.
- **Challenges and learning:** The first focused test run failed for two reasons: one route test had accidentally been rewritten to use a valid Sofia district, and the runtime app title still came from an older local `.env` value. The Windows shell also mangled Cyrillic district names and special characters during an intermediate rewrite, so I switched the catalog and digest code to escaped literals for a stable, encoding-safe result.
- **Evidence:** `app/catalog.py`, `app/config.py`, `app/main.py`, `app/templates/index.html`, `app/email/delivery.py`, `.env.example`, `README.md`, `tests/test_app_routes.py`, `tests/test_email_digest.py`, and the verified command outputs above.

### 2026-06-23 - Newspaper-style email digest aligned to the calmer Sofia UI

- **Outcome:** Reworked the digest email into a calmer editorial layout with paper tones, serif masthead styling, compact listing rows, and a more newspaper-like reading rhythm so the digest feels closer to a real estate section in a daily paper.
- **Approach and reasoning:** Mirrored the updated dashboard tone instead of using a generic promotional email. Kept the subscription summary prominent, made the listing rows denser for long digests, and preserved the unsubscribe action inside the email footer so the workflow stays practical.
- **AI-assisted workflow:** Codex reviewed the current dashboard palette and the email builder, then refactored the digest HTML and text copy to use newspaper-style framing, softer colors, a masthead, editorial labels, and compact listing cards. The unsubscribe button and app delete flow were kept intact.
- **AI tool choice:** Codex was used because the change required coordinated HTML/email rendering, copywriting, and regression testing in the same repository.
- **Key prompts:** "I want the email dogest to match the new UI with calm colors and resonating as if the user is getting a newspaper real estate listing."
- **Validation:** Ran `.\.venv\Scripts\python -m pytest tests\test_email_digest.py tests\test_app_routes.py` and got 13 passing tests with one upstream Starlette deprecation warning. Ran `git diff --check` successfully.
- **Challenges and learning:** Email clients vary widely, so the design had to stay legible and compact without depending on advanced CSS features or layout behavior that could break in inboxes.
- **Evidence:** `app/static/app.css`, `app/email/delivery.py`, `tests/test_app_routes.py`, `tests/test_email_digest.py`, `docs/exam-journal.md`

### 2026-06-23 - Inbox-safe digest layout for the newspaper-style email

- **Outcome:** Replaced the flex-based saved-search summary block with a table-based layout so the email renders consistently in inboxes without the status badge overlapping the subscription title.
- **Approach and reasoning:** Kept the newspaper-like palette and editorial tone, but moved the most fragile part of the layout to table markup because email clients handle tables much more reliably than flexbox. Preserved the unsubscribe button and the compact listing cards.
- **AI-assisted workflow:** Codex used the user screenshot to identify the broken section, then adjusted only the summary block in the digest HTML and verified the result with the existing digest tests.
- **AI tool choice:** Codex was used because this was an inbox-rendering fix that needed local code inspection, HTML adjustment, and immediate regression testing.
- **Key prompts:** "The email looks broken"
- **Validation:** Ran `.\.venv\Scripts\python -m pytest tests\test_email_digest.py` and got `3 passed in 0.39s`.
- **Challenges and learning:** Email rendering remains more conservative than web UI rendering, so visually nice CSS still has to be balanced against what common mail clients actually support.
- **Evidence:** `app/static/app.css`, `app/email/delivery.py`, `tests/test_app_routes.py`, `tests/test_email_digest.py`, `docs/exam-journal.md`

### 2026-06-23 - Unified pill colors in the email digest

- **Outcome:** Made the small pill-style badges in the digest use one shared light color so the saved-search labels, price range, and match count read as one calm visual system.
- **Approach and reasoning:** Removed the mixed pill colors after the inbox screenshot showed too much contrast between the chips. Kept the editorial newspaper look, but reduced the visual noise by making the badges uniform.
- **AI-assisted workflow:** Codex compared the rendered digest with the user screenshot, then updated the badge palette and status chip styling in the email HTML and re-ran the email tests.
- **AI tool choice:** Codex was used because the task was a small rendering refinement that needed code inspection, HTML adjustments, and immediate validation.
- **Key prompts:** "I want the small bubles to be the same light color in the email"
- **Validation:** Ran `\.\venv\Scripts\python -m pytest tests\test_email_digest.py` and got `3 passed in 0.36s`.
- **Challenges and learning:** Even when the visual style is simple, email clients render small UI atoms very differently, so consistency matters more than decorative color variety.
- **Evidence:** `app/static/app.css`, `app/email/delivery.py`, `tests/test_app_routes.py`, `tests/test_email_digest.py`, `docs/exam-journal.md`

### 2026-06-23 - Neutral newsprint palette and tighter classifieds rows

- **Outcome:** Added a subtle "Today's edition" dateline, tightened each listing row, and replaced the yellow-cream paper colors in both the web UI and HTML digest with neutral newsprint white and true-white content surfaces.
- **Approach and reasoning:** Preserved the editorial real-estate newspaper layout while separating the paper effect from yellow tint. Neutral `#f7f7f5` now provides the aged-paper texture, with `#ffffff` cards and controls for clarity.
- **AI-assisted workflow:** Codex refined the digest layout, then incorporated the developer's palette correction across the shared UI stylesheet and inline email-safe HTML colors. Regression assertions now prevent the rejected cream color from returning.
- **AI tool choice:** Codex was used because the correction spanned CSS, email-safe inline HTML, tests, and repository verification.
- **Key prompts:** "ok, do that"; "Make the background white as an old newspaper, not this yellowish nightmare in both the UI and the HTML email template."
- **Validation:** Confirmed no legacy warm-paper colors remain. Ran `.\scripts\run_pytest_clean.ps1 tests\test_app_routes.py tests\test_email_digest.py -q` with `13 passed`, then `.\scripts\run_pytest_clean.ps1 -q` with `23 passed, 1 warning`.
- **Challenges and learning:** The first editorial palette read as unpleasantly yellow. The developer's correction clarified that the newspaper character should come from typography, borders, and texture rather than cream-colored surfaces.
- **Evidence:** `app/static/app.css`, `app/email/delivery.py`, `tests/test_app_routes.py`, `tests/test_email_digest.py`, `docs/exam-journal.md`

### 2026-06-23 - Black-and-white editorial email redesign

- **Outcome:** Reworked the digest into a more restrained editorial style with black-and-white foundations, subtle teal accents, and no cartoonish blue or pink surfaces.
- **Approach and reasoning:** Kept the newspaper-like structure but removed the playful color blocks that made the earlier version feel more like a poster than a print digest. The new version stays aligned to the UI while looking calmer and more premium.
- **AI-assisted workflow:** Codex reviewed the current digest, replaced the loud color blocks with neutral surfaces, adjusted the badge and header treatment, and updated the digest test expectations to match the new palette.
- **AI tool choice:** Codex was used because the task required coordinated HTML, copy, and regression-test changes in one local workspace.
- **Key prompts:** "Change the current email template code to remove the cartoonish elements. Redesign it with a modern, sleek "editorial" aesthetic inspired by classic print newspaper real estate listings and like the New Yorker. I want it still to match the UI but with minimalist black-and-white tones, with the known accents."
- **Validation:** Ran the focused email digest tests and got 3 passing tests.
- **Challenges and learning:** The main challenge was preserving clarity and hierarchy while stripping the palette down to almost monochrome, since the email still needs to feel branded rather than generic.
- **Evidence:** `app/email/delivery.py`, `tests/test_email_digest.py`, `docs/exam-journal.md`

### 2026-06-23 - Lightened the email canvas away from yellow

- **Outcome:** Shifted the digest background and surrounding surfaces to a cleaner neutral white/gray palette so the email reads lighter and stops feeling yellowish.
- **Approach and reasoning:** Preserved the black-and-white editorial direction but removed the warmer cream tones from the outer canvas and summary surfaces. The result stays calm and newspaper-like while feeling fresher in the inbox.
- **AI-assisted workflow:** Codex reviewed the current digest palette, replaced the remaining warm backgrounds with neutral whites, and updated the email digest assertions to match the new surfaces.
- **AI tool choice:** Codex was used because this was a visual refinement that required code inspection and immediate regression testing.
- **Key prompts:** "Ok, I want the background of the template to be lighter and not yellowish"
- **Validation:** Ran `\.\venv\Scripts\python -m pytest tests\test_email_digest.py` and got `3 passed in 0.36s`.
- **Challenges and learning:** Neutral email backgrounds are subtle, but even a small cream tint can dominate the inbox impression when the rest of the design is minimal.
- **Evidence:** `app/email/delivery.py`, `tests/test_email_digest.py`, `docs/exam-journal.md`

### 2026-06-23 - Authenticated multi-user accounts with per-user scheduler and manual job controls

- **Outcome:** Added private user accounts with email verification, login, logout, password reset, account-owned subscriptions, per-user scheduler settings, and per-user manual job execution. The public dashboard is now an authenticated experience, while the one-click email unsubscribe link still deactivates a saved alert without exposing other user data.
- **Approach and reasoning:** Kept the existing FastAPI, SQLite, and Jinja2 stack instead of introducing an external auth dependency. Used server-side opaque sessions with HttpOnly cookies, per-session CSRF tokens, and scrypt password hashing from the Python standard library so the MVP stays exam-friendly and locally runnable. The previous global scheduler configuration was refactored into one scheduler row per user so each verified user can choose their own interval without needing an admin role.
- **AI-assisted workflow:** Codex inspected the public subscription, job, scheduler, and email code paths, then added user/session/token models, a startup schema upgrader for the existing SQLite database, an authentication service, account email messages, ownership checks in the route layer, and a conditional dashboard template for signed-out versus signed-in users. During verification, I corrected two meaningful issues discovered by the tests: SQLite returned naive datetimes for token/session expiry checks, and the reset/verification tests initially parsed the wrong preview email when multiple `.eml` files existed.
- **AI tool choice:** Codex was used because the change crossed backend persistence, security flows, scheduler architecture, HTML templates, client-side dashboard behavior, and automated tests in one local workspace.
- **Key prompts:** "/plan Extend the app, so differnet users can register with their email, log in safely based on modern security authentication standards and architecture."; "Implement the plan with one smal cahnge: I want each user to be able to apply the scheduler and the manual job controls. Not only the admin"
- **Validation:** Ran `powershell -ExecutionPolicy Bypass -File .\scripts\run_pytest_clean.ps1 tests/test_app_routes.py tests/test_scheduler_routes.py tests/test_scheduler_service.py tests/test_email_digest.py -q` and got `14 passed, 1 warning in 4.35s` after the fixes. Then ran `powershell -ExecutionPolicy Bypass -File .\scripts\run_pytest_clean.ps1 -q` and got `20 passed, 1 warning in 5.63s`. Ran `.\\.venv\\Scripts\\python -m ruff check .` and got `All checks passed!`. The remaining warning is the existing upstream `StarletteDeprecationWarning` from FastAPI's installed test client dependency.
- **Challenges and learning:** The Windows sandbox blocked the normal patch utility for this workspace, so implementation had to be finished through carefully scoped local file rewrites. TestClient form posts were kept dependency-free by parsing URL-encoded request bodies directly instead of adding `python-multipart`. The previous scheduler table also hard-coded `id = 1`, which caused a per-user insert collision and had to be removed before per-user schedules could work.
- **Evidence:** `app/models.py`, `app/migrations.py`, `app/services/auth.py`, `app/services/scheduler.py`, `app/services/jobs.py`, `app/services/subscriptions.py`, `app/email/delivery.py`, `app/main.py`, `app/templates/index.html`, `app/templates/reset_password.html`, `app/static/app.css`, `tests/test_app_routes.py`, `tests/test_scheduler_routes.py`, `tests/test_scheduler_service.py`, `tests/test_email_digest.py`, `plans.md`, and the verified command outputs above.
### 2026-06-23 - Final report assembled from verified evidence

- **Outcome:** Prepared the final exam report in `docs/final-project-report.md` using the verified journal, implementation, current test output, personal development notes, and safe working-system screenshots.
- **Approach and reasoning:** Condensed the strongest evidence into six technological modules, kept each module below approximately half a page, and selected registration and scheduler screenshots that do not display the user's email address or an account token. Kept the report candid about the remaining new-only digest limitation.
- **AI-assisted workflow:** Codex followed the project-local `update-exam-evidence` skill, mapped journal entries to the assignment rubric, inspected current implementation and screenshots, redacted an exposed credential from the current notes file, and produced a Google-Docs-ready Markdown report.
- **AI tool choice:** Codex was used because it could correlate conversation history, repository evidence, screenshots, source code, and fresh verification results without inventing missing evidence.
- **Key prompts:** вЂњPrepare the final document using /skills $update-exam-evidenceвЂќ; вЂњI have already done some screenshots in the docs folderвЂќ; вЂњI also have my personal notes in final_project_notex.txt.вЂќ
- **Validation:** Ran `powershell -ExecutionPolicy Bypass -File .\scripts\run_pytest_clean.ps1 -q` and got `20 passed, 1 warning in 8.49s`. Ran `.\.venv\Scripts\python -m ruff check .` and got `All checks passed!`. Visually inspected the selected screenshots.
- **Challenges and learning:** The notes contained a Gmail credential and several screenshots exposed a personal email address or verification token. Those screenshots were excluded from the report, the current note was redacted, and credential rotation plus Git-history cleanup remain mandatory. The report also flags that current digest delivery reloads all stored matches rather than only matches created in the latest run.
- **Evidence:** `docs/final-project-report.md`, `docs/report-screenshots/`, `docs/exam-journal.md`, and the command outputs above.
### 2026-06-23 - Expanded AI workflow narrative and complete screenshot appendix

- **Outcome:** Expanded the final report with the planning-to-execution strategy, project-local subagent and skill design, model/reasoning choices recorded in the developer notes, separate debugging-session lessons, a deeper tool assessment, and every available screenshot artifact.
- **Approach and reasoning:** Treated GPT/model and reasoning-level details as developer-recorded evidence rather than platform telemetry. Distinguished configured subagents from verified invocation because no complete automatic agent-call audit trail exists. Allowed the report to exceed six pages at the developer's explicit request.
- **AI-assisted workflow:** Codex inspected `plans.md`, the three agent TOML files, `.codex/config.toml`, `$fullstack-feature`, the locally installed `beautifulsoup-parsing` skill from skills.sh, the journal, personal notes, and all image/PDF evidence. It rendered all three pages of both digest PDFs and created local privacy-safe copies of all screenshots.
- **AI tool choice:** Codex was used to correlate repository configuration, recorded prompts, model-selection notes, debugging history, and visual evidence. The local BeautifulSoup skill and evidence skill are described as specialized workflow guidance rather than separate AI models.
- **Key prompts:** вЂњTell more about how we created subagents and skillsвЂќ; вЂњTell more about how we used plan mode with GPT 5.5 and high reasoning effortвЂќ; вЂњI want to include all the screenshots.вЂќ
- **Validation:** Verified that `docs/report-screenshots/` contains the registration, verification, reset, dashboard, sale form, rent form, scheduler, stored-alerts image, and all six rendered digest pages. Visually inspected the privacy masks. Application tests were not rerun because this change affects only documentation and generated evidence images.
- **Challenges and learning:** The original screenshots contained an email address, personal name, verification/reset tokens, and Gmail message URLs. The final report uses sanitized copies and keeps the originals out of the embedded public appendix. The expanded report intentionally exceeds the normal page guideline.
- **Evidence:** `docs/final-project-report.md`, `docs/report-screenshots/`, `plans.md`, `.codex/agents/`, `.agents/skills/fullstack-feature/`, `skills/beautifulsoup-parsing/`, and `docs/exam-journal.md`.

### 2026-06-23 - Final report simplified and rewritten in first person

- **Outcome:** Simplified `docs/final-project-report.md` to about 2,090 words, rewrote the narrative consistently from my point of view, and retained the assignment's required modules, AI workflow, prompts, challenges, screenshots, repository link, and future improvements.
- **Approach and reasoning:** Removed repeated architecture and tool discussion while keeping one concise approach, AI-assisted workflow, validation statement, and key-prompt section for each technological module. Updated matching and deduplication to reflect the completed pending/delivered database workflow.
- **AI-assisted workflow:** Codex compared the report with the assignment rubric and exam journal, identified the stale “new listings only” limitation and outdated test count, then rewrote the report and expanded browser validation into a concrete explanation of the local URL, desktop and responsive viewports, checked behaviors, fallback to headless Chrome, and issues found visually.
- **AI tool choice:** Codex was used because the revision required cross-checking narrative claims against repository evidence rather than only proofreading prose.
- **Key prompt:** “Review the final-project-report.md, make it simple and enough to cover the exam, and make it sound from my point of view. The section about browser validation is not clear enough.”
- **Validation:** Confirmed that all screenshot links referenced by the report exist. `git diff --check` reported only the expected Windows LF-to-CRLF warning. Application tests were not rerun because this change affects documentation only; the report cites the latest verified full-suite result of `22 passed, 1 warning in 5.91s`.
- **Challenges and learning:** An additional untracked screenshot could not be privacy-inspected in the current Windows image sandbox, so it was not added to the public report. The report now describes the included images as privacy-safe evidence rather than claiming every folder artifact is included.
- **Evidence:** `docs/final-project-report.md`, `docs/exam-journal.md`, `docs/report-screenshots/`, and the report-link and diff checks above.

### 2026-06-23 - Redacted signed-in account screenshot added to report

- **Outcome:** Added a privacy-safe signed-in account screenshot to the final report, showing that subscriptions, manual runs, and scheduler settings belong to the authenticated account.
- **Approach and reasoning:** Covered the complete email address with an opaque black rectangle, saved the result under an explicitly redacted filename, and moved the unredacted source out of the repository to prevent accidental publication.
- **AI-assisted workflow:** Codex loaded the local screenshot into the conversation after the Windows image sandbox blocked direct inspection, used the image-editing tool to create the redaction, visually checked the result, saved the selected output in the report assets, and added its Markdown reference.
- **AI tool choice:** The image-editing tool was used because the task required modifying a raster screenshot while preserving the visible UI evidence.
- **Key prompt:** “Try redacting and adding the untracked screenshot again.”
- **Validation:** Confirmed visually that the email address is fully covered and that the account heading, ownership explanation, and logout control remain visible. Confirmed that the report references the new redacted asset and that the unredacted source no longer appears in the repository worktree.
- **Challenges and learning:** Direct `view_image` and file-path image editing were blocked by the Windows split-root sandbox, so the source image had to be loaded as image data before editing.
- **Evidence:** `docs/report-screenshots/04-signed-in-account-redacted.png`, `docs/final-project-report.md`, and `docs/exam-journal.md`.

### 2026-06-23 - Local final report synchronized from the Google Doc

- **Outcome:** Updated `docs/final-project-report.md` to match the user-edited Google Doc exactly in wording, section order, table contents, future improvements, and screenshot order. The Google Doc itself was not edited.
- **Approach and reasoning:** Treated the Google Doc as the read-only source of truth, downloaded a temporary DOCX export, read its paragraph, table, and image relationships directly, and rebuilt the Markdown from that structure.
- **AI-assisted workflow:** Codex attempted read-only access through the in-app browser and standard page reader, then used Google's read-only export endpoint when those paths were unavailable. The DOCX was inspected in three bounded structural sections before the local report was patched.
- **AI tool choice:** Codex was used because the task required live document retrieval, DOCX structure inspection, local Markdown editing, and exact comparison in one workflow.
- **Key prompt:** “Do not edit the Google Doc, but rather make the .md file match exactly the doc.”
- **Validation:** Compared 131 normalized Google Doc text blocks with 131 Markdown text blocks and found zero wording differences. Compared all 13 embedded DOCX images with their local report assets using SHA-256 and found exact matches.
- **Challenges and learning:** The in-app browser connection was unavailable and the standard page reader returned a 403 response. The read-only Google Docs export endpoint provided the authoritative content without modifying the document.
- **Evidence:** `docs/final-project-report.md`, `docs/report-screenshots/`, `docs/exam-journal.md`, the verified comparison output, and the Google Drive URL above.

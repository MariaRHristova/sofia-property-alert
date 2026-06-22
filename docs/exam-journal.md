# Bulgaria Property Alert - Exam Journal

This journal contains raw, verified evidence for the AI-Assisted Development exam report. It is intentionally more detailed than the final submission.

## Project summary

- **Repository:** https://github.com/MariaRHristova/sofia-property-alert
- **Goal:** Let users define criteria for Bulgaria real estate and receive daily email notifications for newly discovered matching listings.
- **Final submission:** TODO - Google Drive document URL

## Module status

| Module | Status | Strongest evidence |
| --- | --- | --- |
| UI and validation | In progress | `app/main.py`, `app/templates/index.html`, `app/schemas.py`, `tests/test_app_routes.py` |
| Database layer | In progress | `app/models.py`, `app/db.py`, `app/services/subscriptions.py` |
| Listing provider and parsing | Complete | `app/providers/parsers.py`, `app/providers/fixtures.py`, `app/services/listings.py`, `tests/test_fixture_parser.py` |
| Matching and deduplication | In progress | `app/services/preview.py`, `app/services/jobs.py` |
| Scheduler | Not started | TODO |
| Email delivery | In progress | `app/email/delivery.py`, `app/services/jobs.py`, `tests/test_email_digest.py` |
| Testing and observability | In progress | `tests/conftest.py`, `tests/test_fixture_parser.py`, `tests/test_app_routes.py` |

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
- **Validation:** Ran `git diff --check` successfully, reviewed the complete patch, and confirmed that AGENTS.md contains no copied Node/TypeScript commands or unresolved template placeholders.
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
- **Key prompts:** "I want the app to search the site live."; "Try subscribe to mhristova27@gmail.com for Sale, apartments in Sofia ??????? distict for minimum of 100 000 Euros."; "For Sofia the discticts are given in the HTML here "https://www.imot.bg/search/prodazhbi/grad-sofiya""
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

## Challenges and tool comparison notes

- Repository setup required a fallback from unavailable GitHub CLI/browser automation to Git Credential Manager.

## Working-system evidence checklist

- [ ] Screenshot 1: user-facing workflow
- [ ] Screenshot 2: email, tests, API result, or job logs
- [x] Public GitHub repository linked
- [x] No secrets or personal data visible

## Final report checklist

- [ ] Project idea and requirements fit within one page
- [ ] Each module description is no longer than half a page
- [ ] Approach, workflow, tests, tool choice, and prompts are covered
- [ ] Biggest challenges and AI-tool comparison are included
- [ ] Future improvements are included
- [ ] At least two working-system screenshots are included
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

# AI-Assisted Development Final Exam

# Sofia Property Alert

23 June 2026

Mariya Hristova

**Public repository:** <https://github.com/MariaRHristova/sofia-property-alert>

## 1. Project idea and requirements

Sofia Property Alert was created for people who repeatedly search for real estate in Sofia. A registered user can save criteria such as sale or rent, property type, rooms, Sofia districts, price, and minimum area. The application collects listings from imot.bg, compares them with the user’s saved alerts, and sends an email digest containing only matches that have not already been delivered.

The proof of concept is deliberately limited to Sofia so district names and generated search URLs stay consistent with the live imot.bg structure. A fixture-backed provider also supports reliable demonstrations and tests without depending on an external website.

### Functional requirements

- Register with an email address, verify the account, log in, log out, and reset a forgotten password.
- Keep every user's alerts, job history, and schedule private.
- Create, deactivate, reactivate, and permanently delete a search alert.
- Search by listing type (buy or rent), property type, number of rooms, Sofia districts, price range, and minimum area.
- Collect, parse, and normalize listings from imot.bg; the provider is pluggable so fixtures or alternative sources may be used for deterministic tests.
- Run the listing job manually or automatically for each user.
- Sends an email digest of newly matched listings for each saved alert (HTML + plain-text). Previews are written as local .eml files for testing; SMTP delivery is available via configuration.
- Avoid duplicate matches and emails: if a listing was already recorded for an alert, it won’t be added again or shown in later digests for the same user.

## 2. Architecture and technological modules

### Architecture layers

- **Presentation:** FastAPI routes + templates (HTTP handlers, forms).
- **Application / Services:** SubscriptionService, JobService, MatchingService (business logic, idempotency).
- **Domain / Models:** SQLAlchemy domain models and validation (Pydantic schemas at boundaries).
- **Integration / Providers:** Provider implementations (fixture, imot.bg), HTTP fetching, parsing.
- **Infrastructure:** Scheduler, email delivery, storage, configuration, and test fixtures.

### Module 1 — Web interface, accounts, and validation

**Approach.** Server-rendered Jinja2 pages were chosen instead of adding a JavaScript framework. The application uses opaque server-side sessions, HttpOnly cookies, CSRF tokens, email verification and reset tokens, and scrypt password hashing. Alerts and job controls are scoped to the signed-in user.

**AI-assisted workflow.** Codex first supported implementation of the alert form and routes, followed by private accounts and user-controlled manual and scheduled jobs. Tests exposed two problems: SQLite returned naive datetimes during token checks, and account tests sometimes selected the wrong preview email. Both issues were reviewed and corrected before completion.

**Validation.** tests/test_app_routes.py covers registration, verification, login, password reset, ownership, alert management, and validation errors.

**Key prompts:** “Extend the app, so different users can register with their email and log in safely”; “Each user should be able to apply the scheduler and the manual job controls.”

### Module 2 — Database, matching, and deduplication

**Approach.** SQLAlchemy models store users, sessions, tokens, alerts, listings, matches, job runs, and per-user scheduler settings. A listing is unique by source and external ID, and a listing-alert pair is also unique. The job loads only match rows whose state is pending and which have no delivery timestamp. After a successful send it marks those rows as delivered; a failed send leaves them pending for retry.

**AI-assisted workflow.** Codex supported the separation of persistence and matching from the HTTP routes, followed by reversible unsubscribe, permanent deletion, and new-match-only delivery. The database match table was selected as the source of truth because it is safer than inferring delivery history from the latest scraper response.

**Validation.** tests/test_job_service.py proves that a repeated listing is not sent again, a later new listing is sent by itself, and a failed delivery remains pending until a successful retry.

**Key prompts:** “Unsubscribe should deactivate the alert and allow subscribing again”; “Can this be handled by the database layer—send only listings not sent in previous runs?”

### Module 3 — Listing provider and BeautifulSoup parser

**Approach.** Source-specific behavior is hidden behind a ListingProvider interface. FixtureListingProvider gives deterministic local results. ImotBgListingProvider builds Sofia search URLs, follows pagination, and returns normalized listing candidates. The parser extracts stable IDs, canonical URLs, district, price, area, rooms, transaction type, and property type while skipping duplicates and sponsored content.

**AI-assisted workflow.** The first selectors matched the sample fixture but not the live site. The project-local beautifulsoup-parsing skill from skills.sh guided safer DOM navigation, missing-field handling, URL resolution, text cleanup, and respectful requests. Codex then helped align the parser and district catalog with the supplied Sofia pages. A separate debugging session showed that one apparent scraper failure was actually caused by fixture mode.

**Validation.** tests/test_fixture_parser.py parses saved HTML, so the automated suite never depends on the live website. Live access remains configuration-controlled.

**Key prompts:** “Use the BeautifulSoup parsing skill to plan how to implement the search properly”; “The filters do not match the imot.bg structure.”

### Module 4 — Job execution and per-user scheduling

**Approach.** Manual and scheduled runs call the same pipeline. It loads the current user's active alerts, collects and persists listings, creates new matches, builds digests, records delivery results, and stores counts and errors. APScheduler supports every N minutes or one daily time in Europe/Sofia. A per-user lock prevents overlapping runs.

**AI-assisted workflow.** The first plan used a single global schedule. When accounts were added, Codex helped redesign it as one persisted schedule per user while preserving the manual button. Immediate “Preparing your digest” feedback was also added because the button previously appeared unresponsive.

**Validation.** tests/test_scheduler_service.py checks disabled schedules, registration, and overlap prevention. tests/test_scheduler_routes.py checks authenticated per-user configuration.

**Key prompts:** “I want to be able to choose the time interval the job runs”; “When I click Run daily job, the user must know that something is happening.”

### Module 5 — Email rendering and delivery

**Approach.** The email builder produces HTML and plain text. Delivery can write a local .eml preview or use SMTP settings from the environment. This separation supports inspection and testing of a real message without committing credentials or contacting Gmail during tests. Verification and password-reset messages use the same delivery service.

**AI-assisted workflow.** Codex supported the preview and SMTP paths, Gmail authentication diagnosis, and visible delivery errors. Screenshot-based iterations refined the digest until it matched the application's restrained newspaper style. A flex layout was replaced with table markup after Gmail rendered the original layout incorrectly.

**Validation.** tests/test_email_digest.py verifies listing and empty-result messages, subjects, text alternatives, unsubscribe links, and the approved neutral palette. Test configuration always uses temporary preview output instead of real SMTP.

**Key prompts:** “Add a real email preview/delivery path”; “If there are no listings, also send an email”; “Make the email match the UI style.”

### Module 6 — Testing and operational safety

**Approach.** Pytest uses temporary SQLite databases, saved HTML, fake delivery results, and temporary email-preview folders. scripts/run_pytest_clean.ps1 removes generated test data after every run. Secrets come from environment variables and .env is excluded from Git.

**AI-assisted workflow.** Each feature was checked with focused tests before running the clean full-suite script. Development evidence was maintained in docs/exam-journal.md with the project-local update-exam-evidence skill, recording actual commands, failures, corrections, and screenshots.

**Validation on 23 June 2026.**

```text
powershell -ExecutionPolicy Bypass -File .\scripts\run_pytest_clean.ps1 -q
22 passed, 1 warning in 5.91s
```

The remaining warning is an upstream Starlette deprecation warning. A focused Ruff check of the delivery-state implementation and tests returned All checks passed!.

**Key prompt:** “Add a hook when you do tests to clean up the test data.”

## 3. AI-assisted development workflow

### AI-assisted planning and execution strategy

Codex was used because it provided the capabilities required and a paid subscription allowed me access to frontier models, which made high-reasoning Plan mode practical for ambiguous architecture decisions. Strategic planning was deliberately separated from implementation. The initial architecture and execution plan were drafted in Plan mode (GPT 5.5, high reasoning) and the approved plan was saved as plans.md so the strategy lives in the repository rather than only in chat.

After plan approval, implementation moved to lower-cost configurations: the initial scaffold used GPT 5.4 (medium reasoning), and most small iterations used GPT 5.4 mini (low reasoning). Higher-reasoning runs were reserved for changes that affected architecture - for example, designing per-user authentication and scheduling. The resulting pattern was simple and practical: invest heavier reasoning where ambiguity and cross-module trade-offs matter, and use lighter, cheaper runs for routine, well-scoped edits (templates, selectors, focused tests).

| Development phase | Recorded Codex configuration | Purpose and evidence |
| --- | --- | --- |
| Project planning | GPT 5.5, high reasoning, Plan mode | Defined MVP scope and modules; saved the approved result in plans.md. |
| Agent and workflow design | GPT 5.5, medium reasoning | Created project-local backend, frontend, and integration-review agents plus the $fullstack-feature skill. |
| Initial implementation | GPT 5.4, medium reasoning | Translated the approved plan into the FastAPI/SQLAlchemy/Jinja2 scaffold and tests. |
| Small implementation iterations | GPT 5.4 mini, low reasoning | Used for narrower parser, catalog, UI, and debugging edits after the contract was understood. |
| Complex extensions | Higher-reasoning planning followed by focused execution | Used for scheduler design and authenticated multi-user ownership. |
| Debugging | Separate focused sessions | Isolated email, live scraping, UI/browser, scheduler, and authentication problems. |

Three project-local subagents were created to make responsibilities explicit:

- backend_engineer owned FastAPI contracts, SQLAlchemy/SQLite, providers, matching, scheduling, and email business logic.
- frontend_engineer owned Jinja2 templates, form behavior, accessibility, loading/error states, responsive design, and browser verification.
- integration_reviewer was read-only and configured for high reasoning so it could inspect cross-layer contracts, idempotency, security, and test evidence without changing files.

.codex/config.toml limited the design to four concurrent threads and one level of delegation. The project-local $fullstack-feature skill required alignment of backend and frontend interfaces — agreeing on endpoints, payloads, and expected behavior — before implementation, and subagents were reserved only for changes that genuinely crossed layers. That configuration proved useful, but proving agent invocation later was difficult: Codex does not provide a reliable debug or per-call audit mode for tracking tool or agent calls. For that reason this report distinguishes configured agent capability from verified use and does not claim every feature was implemented by a subagent.

Local skills supported the workflow. $fullstack-feature described safe multi-agent coordination. The update-exam-evidence skill maintained a running log of prompts, commands, and results to simplify exam preparation. The beautifulsoup-parsing skill was installed locally from skills.sh/mindrally/skills/beautifulsoup-parsing and used to guide DOM navigation, safe extraction, URL resolution, missing-field handling, parser choice, and respectful scraping.

## 4. Challenges, tool assessment, and learning

### 4.1 Turning an open idea into an executable plan

The original idea sounded simple: select criteria and receive new Sofia listings by email. In practice it contained at least seven modules - UI validation, accounts, persistence, parsing, matching, scheduling, and email -and several safety questions. Plan mode with GPT 5.5 and high reasoning was most valuable at this stage because the problem was still ambiguous. It produced an ordered implementation strategy and saved it in plans.md. Persisting the plan made later sessions less dependent on chat memory and gave Codex a shared checkpoint between sessions.

A useful lesson was that reasoning effort should follow uncertainty. High reasoning added value when deciding module boundaries, fixture/live architecture, per-user scheduling, and authentication ownership. It was wasteful for repetitive edits after those decisions were stable. GPT 5.4 medium and GPT 5.4 mini/low reasoning were therefore used for narrower execution iterations. This was not only a cost decision; it reduced the tendency to redesign settled parts of the MVP.

### 4.2 Building and evaluating project-local subagents

Creating the subagents required inspecting the real repository first. The backend agent was specialized for Python 3.11, FastAPI, SQLAlchemy, SQLite, APScheduler, BeautifulSoup, fixture tests, and email boundaries. The frontend agent was specialized for a server-rendered Jinja2 interface rather than assuming React. The integration reviewer was deliberately read-only, with high reasoning, so review could not accidentally modify the implementation it was evaluating.

The $fullstack-feature skill acted as an orchestrator: backend and frontend agents were expected to propose one compatible contract before implementation, and the reviewer checked the integrated diff afterward. Concurrency was capped at four threads and depth at one. These limits prevented uncontrolled agent trees.

The experiment also revealed weaknesses. Merely defining an agent does not ensure that the primary agent will invoke it, and the Codex interface did not provide me with a simple permanent audit trail of every agent and skill call. On some full-stack iterations, coordination consumed context quickly and produced conflicting route variants that the primary agent then had to reconcile. What I learned is the hard-earned lesson  that an ill-defined agent can be more work than help. For this project, the best use of subagents was substantial, clearly separated work; small changes were better handled directly. In practice, broad subagent orchestration sometimes consumed excessive context for small tasks, so direct single-agent work with focused skills often proved more efficient.

### 4.3 Using a downloaded skill for the BeautifulSoup scraper

The BeautifulSoup task benefited from a specialized external skill. I found mindrally/skills/beautifulsoup-parsing on skills.sh and installed it locally under skills/beautifulsoup-parsing/. Keeping it project-local made its instructions reproducible and avoided changing the global Codex environment.

The skill was not treated as a finished scraper. It supplied parsing practices: choose lxml, navigate with stable selectors, handle missing elements, clean text, resolve relative URLs, validate types, deal with malformed HTML and encoding, use an explicit user agent, and respect site terms and rate limits. Codex then applied those practices to the actual imot.bg pages supplied.

The first implementation still failed because its fixture selectors did not represent the live result cards. Later, live results appeared absent because the application was still configured for the fixture provider. These were two different problems- parser correctness and runtime provider selection- and separate debugging sessions were needed to distinguish them. The final design keeps both providers: live mode for demonstration and fixtures for deterministic tests.

### 4.4 Separate debugging sessions: useful focus, costly context

Separate sessions were used for the inert subscription button, email preview versus real SMTP delivery, Gmail authentication, live scraper activation, imot.bg filter alignment, scheduler behavior, browser verification, visual design, and later authentication. This helped isolate one failure at a time and allowed different reasoning levels to be chosen for different problems.

The drawback was context fragmentation. A new session did not automatically know which settings, branch of behavior, or previous failed attempt mattered. For example, one session interpreted “no results” as a parser issue before discovering fixture mode; another needed to rediscover the distinction between preview output and SMTP sending. AGENTS.md, plans.md, tests, and docs/exam-journal.md gradually became the durable memory between sessions. This is one of the clearest benefits of repository-local instructions: they reduce dependence on the model's conversational memory.

### 4.5 Email delivery, credentials, and inbox rendering

Email combined security, external configuration, and presentation. Preview mode was initially useful but did not satisfy the requirement to send mail. Gmail SMTP then introduced app-password and authentication debugging.

Inbox HTML created a different class of issue. Flexbox that looked correct in a browser overlapped in the email client, so it was replaced with table-based markup. Bright colors that looked energetic in the application felt distracting in a digest; repeated screenshot feedback moved both surfaces toward restrained newspaper typography and neutral colors.

### 4.6 Overall tool assessment

**Most helpful tool:** Codex was the central tool because it joined planning, repository inspection, editing, terminal execution, debugging, browser-oriented work, and evidence documentation. Its greatest strength was not any single code suggestion but the closed loop from requirement to change to test result.

**Most helpful specialized skill:** beautifulsoup-parsing made the scraper workflow more disciplined and helped translate generic DOM practices into the real imot.bg structure.

**Most helpful artifact:** plans.md was the bridge between high-reasoning planning and lower-cost execution. AGENTS.md became the bridge between separate sessions.

**Least efficient approach:** Broad multi-agent work on small features. It consumed context, made attribution unclear, and sometimes produced contracts that required reconciliation. The improvement is to delegate only independent, bounded subtasks and record the agent assignment and result in the audit trail.

**Model/reasoning lesson:** High reasoning is best for ambiguity, architecture, and review. Medium reasoning works well for coordinated implementation. Mini/low reasoning is effective for small changes after the contract is fixed. Tests, not reasoning level, determine whether execution is acceptable.

## 5. Future improvements

1. Replace Gmail password-based SMTP with OAuth 2.0 or a transactional email provider.
2. Add structured logs and a clearer user-visible run history with delivery status.
3. Move scheduled execution to a continuously hosted worker because local schedules stop when the application stops.
4. Add more search alert filters for sponsored results, floor, year when the building was uilt, etc.
5. Add favorites, notes, price history, and saved-listing comparisons after the exam MVP.
6. Add more cities, not just Sofia

## 6. Working-system evidence

The appendix includes every screenshot artifact prepared for the project. Privacy-safe copies are used here: personal email addresses,name, verification/reset tokens, and Gmail message URLs are covered.

### 6.1 Account registration, login, and recovery

![Account registration, login, and recovery](report-screenshots/01-register-login.png)

### 6.2 Registration verification email

![Registration verification email](report-screenshots/02-verification-email.png)

### 6.3 Password reset email

![Password reset email](report-screenshots/03-password-reset-email.png)

### 6.4 Authenticated home dashboard

![Authenticated home dashboard](report-screenshots/04-home-dashboard.png)

![Signed-in account ownership with private email redacted](report-screenshots/04-signed-in-account-redacted.png)

### 6.5 Creating a sale alert

![Creating a sale alert](report-screenshots/05-create-sale-alert.png)

### 6.6 Creating a rent alert

![Creating a rent alert](report-screenshots/06-create-rent-alert.png)

### 6.7 Per-user scheduler

![Per-user scheduler](report-screenshots/07-scheduler.png)

### 6.8 Stored alerts and live matches

![Stored alerts and live matches](report-screenshots/08-stored-alerts.png)

### 6.9 Rent digest delivered to Gmail

![Rent digest delivered to Gmail, page 1](report-screenshots/09-digest-1-page-1.png)

![Rent digest delivered to Gmail, page 2](report-screenshots/09-digest-1-page-2.png)

### 6.10 Sale digest delivered to Gmail

![Sale digest delivered to Gmail, page 1](report-screenshots/010-digest-2-page-1.png)

![Sale digest delivered to Gmail, page 2](report-screenshots/010-digest-2-page-2.png)

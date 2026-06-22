# Bulgaria Property Alert Execution Plan

## Goal

Build a local-demo MVP where a user can define real-estate criteria for major Bulgaria cities and receive one daily email digest with newly discovered matching listings.

## Agreed scope

- Geography: major cities first (`Sofia`, `Plovdiv`, `Varna`, `Burgas`)
- User model: email form, no accounts
- Source strategy: fixture-first provider plus optional live adapter
- First-run behavior: establish a baseline without sending email
- Notifications: daily digest, duplicate-safe, tokenized unsubscribe
- Deployment target: local demo
- Email mode: preview first, SMTP configurable later

## Execution order

### 1. Repository and project foundation

- Keep `Project-Assignment.docx` unchanged.
- Maintain this plan in `plans.md`.
- Keep `docs/exam-journal.md` updated for meaningful milestones.
- Normalize repository docs and project naming to `Bulgaria Property Alert`.
- Create the Python project scaffold and dependency manifest.

### 2. Application skeleton

- Create a FastAPI application with:
  - `GET /` for the subscription page
  - `POST /subscriptions` to create a subscription
  - `POST /subscriptions/{token}/unsubscribe` to disable a subscription
  - `GET /health` for a health check
- Use Jinja2 templates and Bootstrap for a simple local UI.
- Add configuration via environment variables and `.env.example`.

### 3. Persistence layer

- Use SQLite with SQLAlchemy.
- Introduce these tables:
  - `subscriptions`
  - `listings`
  - `listing_matches`
  - `job_runs`
- Enforce uniqueness so repeated runs cannot resend the same listing.

### 4. Search criteria model

- Support:
  - email
  - sale or rent
  - apartment or house
  - city
  - districts
  - minimum and maximum EUR price
  - room count
  - minimum area
- Keep a versioned local catalog of supported cities and districts for the MVP.

### 5. Provider abstraction and parsing

- Create a `ListingProvider` interface.
- Implement a fixture-backed provider first.
- Implement HTML parsing with BeautifulSoup and `lxml` using safe extraction helpers.
- Keep a future `imot.bg` live adapter behind explicit configuration and respectful access checks.

### 6. Matching and deduplication

- Normalize provider output before matching.
- Re-evaluate all active subscriptions locally against normalized listings.
- Mark matches as baseline on first run and avoid sending email for them.
- Send only genuinely new matches on later runs.

### 7. Email rendering and delivery

- Render email HTML separately from delivery.
- Default to a preview backend that writes digest previews locally.
- Add SMTP configuration for later real delivery when explicitly approved.

### 8. Scheduled workflow

- Add a CLI command for the daily run.
- Add APScheduler with `Europe/Sofia` timezone.
- Keep the scheduler disabled by default in tests.

### 9. Testing and evidence

- Use saved HTML fixtures for parser tests.
- Use temporary databases and fake email delivery in tests.
- Cover:
  - parser behavior
  - missing fields
  - matching boundaries
  - duplicate prevention
  - baseline behavior
  - unsubscribe flow
- Capture at least two screenshots once the MVP works.

## Immediate implementation sequence

1. Save this plan.
2. Scaffold the Python project and dependency manifest.
3. Implement the provider interface and fixture-backed BeautifulSoup parser.
4. Add initial database models and health route.
5. Add focused tests for the parser and fixture provider.
6. Update the exam journal with verified evidence for this milestone.

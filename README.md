# Sofia Property Alert

A web application for creating real-estate search criteria for Sofia, Bulgaria and receiving a daily email with newly discovered matching listings.

## Project status

Initial project setup. Architecture and implementation are in progress.

## Planned MVP

- Create a property search subscription
- Filter by transaction type, property type, district, price, rooms, and area
- Collect and normalize new listings
- Avoid duplicate notifications
- Send a daily email digest
- Support deterministic tests with saved listing fixtures

## Technology

The planned stack is Python, FastAPI, Jinja2, SQLAlchemy, SQLite, APScheduler, and Pytest.

## Exam evidence workflow

Development evidence is recorded in `docs/exam-journal.md`. The project-local `update-exam-evidence` skill in `skills/update-exam-evidence/` defines when and how to update the journal without modifying the original assignment document.

### TEST 

# Bulgaria Property Alert - Exam Journal

This journal contains raw, verified evidence for the AI-Assisted Development exam report. It is intentionally more detailed than the final submission.

## Project summary

- **Repository:** https://github.com/MariaRHristova/sofia-property-alert
- **Goal:** Let users define criteria for Bulgaria real estate and receive daily email notifications for newly discovered matching listings.
- **Final submission:** TODO - Google Drive document URL

## Module status

| Module | Status | Strongest evidence |
| --- | --- | --- |
| UI and validation | In progress | `app/main.py`, `tests/test_app_routes.py` |
| Database layer | In progress | `app/models.py`, `app/db.py` |
| Listing provider and parsing | In progress | `app/providers/`, `tests/test_fixture_parser.py` |
| Matching and deduplication | Not started | TODO |
| Scheduler | Not started | TODO |
| Email delivery | Not started | TODO |
| Testing and observability | In progress | `tests/test_fixture_parser.py`, `tests/test_app_routes.py` |

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

## Challenges and tool comparison notes

- Repository setup required a fallback from unavailable GitHub CLI/browser automation to Git Credential Manager.

## Working-system evidence checklist

- [ ] Screenshot 1: user-facing workflow
- [ ] Screenshot 2: email, tests, API result, or job logs
- [x] Public GitHub repository linked
- [ ] No secrets or personal data visible

## Final report checklist

- [ ] Project idea and requirements fit within one page
- [ ] Each module description is no longer than half a page
- [ ] Approach, workflow, tests, tool choice, and prompts are covered
- [ ] Biggest challenges and AI-tool comparison are included
- [ ] Future improvements are included
- [ ] At least two working-system screenshots are included
- [ ] Google Drive sharing is set to anyone with the link can view
- [ ] Total length is three to six pages

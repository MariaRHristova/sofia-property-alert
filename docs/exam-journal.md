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

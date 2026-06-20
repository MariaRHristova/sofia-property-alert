# Sofia Property Alert — Exam Journal

This journal contains raw, verified evidence for the AI-Assisted Development exam report. It is intentionally more detailed than the final submission.

## Project summary

- **Repository:** https://github.com/MariaRHristova/sofia-property-alert
- **Goal:** Let users define criteria for Sofia real estate and receive daily email notifications for newly discovered matching listings.
- **Final submission:** TODO — Google Drive document URL

## Module status

| Module | Status | Strongest evidence |
| --- | --- | --- |
| UI and validation | Not started | TODO |
| Database layer | Not started | TODO |
| Listing provider and parsing | Not started | TODO |
| Matching and deduplication | Not started | TODO |
| Scheduler | Not started | TODO |
| Email delivery | Not started | TODO |
| Testing and observability | Not started | TODO |

## Development log

### 2026-06-20 — Repository and evidence workflow setup

- **Outcome:** Created the public project repository, added the initial project documentation, and established a project-local workflow for collecting exam evidence.
- **Approach and reasoning:** Used a Markdown journal as the evidence source because it is reviewable in Git and can later be condensed into the required Google Drive document. Preserved the assignment DOCX unchanged.
- **AI-assisted workflow:** Extracted the assignment requirements, mapped the application idea to suitable modules, initialized Git, prepared the README and ignore rules, connected the GitHub remote, and designed the evidence skill.
- **AI tool choice:** Codex was used for repository setup, requirements analysis, workflow design, and verification because it could inspect and modify the local workspace and run Git commands.
- **Key prompts:** “Read the Project_Assignment.docx and help me make a plan how to pass the exam.”; “I would like to create a github repository for the project first.”; “Create the skill that you suggested for this project.”
- **Validation:** Confirmed that local `main` tracks `origin/main` and that the initial commit was pushed successfully. Ran the skill validator successfully (`Skill is valid!`) and checked the patch for whitespace errors.
- **Challenges and learning:** GitHub CLI and browser automation were unavailable, so HTTPS authentication through Git Credential Manager was used for the initial push.
- **Evidence:** `README.md`, `.gitignore`, `AGENTS.md`, `docs/exam-journal.md`, `skills/update-exam-evidence/`, commit `bb80c9d`, and https://github.com/MariaRHristova/sofia-property-alert

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

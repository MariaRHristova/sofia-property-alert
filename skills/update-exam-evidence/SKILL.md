---
name: update-exam-evidence
description: Maintain the Sofia Property Alert AI-Assisted Development exam evidence in docs/exam-journal.md. Use after completing or testing a project module, making an important architecture decision, resolving a meaningful challenge, comparing AI tools, or capturing working-system evidence, and before preparing the final 3-6 page Google Drive document. Do not invoke for trivial formatting-only changes.
---

# Update Exam Evidence

Keep a factual, chronological development record that can be condensed into the final exam document. Treat `docs/exam-journal.md` as the source of truth; do not edit `Project-Assignment.docx`.

## Workflow

1. Read `references/assignment-rubric.md` and the existing journal.
2. Inspect the relevant implementation, Git diff or commit, and test output. Use conversation context for AI interactions and prompts.
3. Decide whether the work is meaningful evidence. Record completed modules, important decisions, tests, failures, corrections, tool comparisons, and screenshots. Skip trivial edits.
4. If the journal does not exist, copy the structure from `assets/exam-journal-template.md`.
5. Append one entry under **Development log** using the journal's entry format.
6. Update the module status table and evidence checklist when their state changed.
7. Keep journal changes with the implementation changes. Do not create a separate commit unless the user requests one.

## Evidence Rules

- Record only claims supported by code, commands, test output, screenshots, commits, or the conversation.
- Never invent prompts, test results, screenshots, dates, tool usage, or implementation details.
- Quote a prompt only when its wording is available. Otherwise label it **Reconstructed prompt**.
- Name the AI tool actually used. Do not substitute a tool merely because the assignment lists it.
- Distinguish AI suggestions from decisions and corrections made by the developer.
- Record failed approaches when they demonstrate debugging or tool evaluation.
- Use paths relative to the repository and include a commit hash when one exists.
- Mark unfinished evidence as `TODO`; do not present it as complete.
- Never include secrets, tokens, credentials, personal data, or sensitive environment values.

## Entry Quality

Keep each entry compact but specific enough to answer the rubric:

- **Outcome**: What now works or what decision was reached?
- **Approach and reasoning**: Why was this design chosen?
- **AI-assisted workflow**: What was requested, reviewed, and changed?
- **AI tool choice**: Which tool was used and why?
- **Key prompts**: Up to three useful interactions.
- **Validation**: Exact tests or manual checks and their results.
- **Challenges and learning**: Failures, limitations, or corrections.
- **Evidence**: Relevant files, commit, logs, and screenshot paths.

Prefer concise bullet points over narrative prose. The journal may be longer than the final report; preserve strong raw evidence and defer compression until final assembly.

## Final Report Preparation

When asked to prepare the submission:

1. Select the strongest entries for each technological module.
2. Condense them to at most half a page per module.
3. Include the project idea and requirements in at most one page.
4. Add challenges, AI-tool comparison, improvements, at least two working-system screenshots, and the public GitHub URL.
5. Keep the total document between three and six pages.
6. Flag any unsupported or missing requirement before claiming the report is ready.


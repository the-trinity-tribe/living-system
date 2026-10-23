# Changelog

All notable changes. Dates are when a version was prepared. Versions before 1.0 are experimental: details may change between them.

## 0.2.0 (unreleased)

From a governance demo to a workspace you can install and grow.

### Added

- **Your own workspace:** `tools/living.py init` creates a private workspace in a separate folder (never inside this repository), with nothing half-made if it fails. `INSTALL.md` lets Claude Code or Codex guide you through it with at most five questions.
- **Profiles:** `student`, `professional`, `employee`, `manager`, each with small starting files and personal goals kept apart from shared rules (`me/`, private by default for employees).
- **Language choice**, with German and Polish starter files (`core/i18n/`), and an optional **calm replies** setting for shorter, plainer agent answers. The agent's rule files stay English in every language. The value check accepts German and Polish column names and score words.
- **Value check:** a 10-minute before/after test you run yourself, and `value-score` to count the results.
- **Handover note:** `handover/LATEST.md`, so the next session (with any agent) starts where the last one stopped.
- **Decision kinds:** proposals can now add a first rule (`kind: new`), replace a rule completely (`kind: replace`) or retire one (`kind: retire`), besides adding an exception. Old decision files are never edited.
- **Optional modules:** `modules`, `add`, `remove`, with five modules: `weekly-update`, `meeting-notes`, `staged-learning`, `knowledge-inbox`, `second-check`. Plans are shown before anything is written; removal keeps files you edited and never touches decisions, proposals or projects. New workspaces list the available modules in `.living/catalog.md`.
- **Workflow generator:** `new-workflow` creates a staged workflow folder in the style of Interpretable Context Methodology (see `CREDITS.md`).
- **`doctor`:** a read-only health check in plain words.
- **Export:** `living.py export` packs a workspace into one zip (without machine-specific files); `upgrade` on a restored copy records the new computer's Living System folder.
- **Decision history:** `review.py history` shows every decision, what is in force, and what amended, replaced or retired each older one.
- **`status`:** what needs your attention (proposals to review, drafts, the last next step), with the exact review command for each waiting proposal.
- **Obsidian guide:** how to open a workspace as an Obsidian vault, approve drafts through the `status` property, and what not to edit by hand; workspace `.gitignore` leaves out Obsidian's window layout files.
- **Shared skills** for Claude Code and Codex (`living-status`, `first-decision`, `propose-change`, `wrap-up`, `catch-up`, `practice`, `share-knowledge`, `onboarding`, `make-the-case`): one source in `core/skills/`, copied to `.claude/skills/` and `.agents/skills/` by `init` and `upgrade`, so both agents get the same short procedures.
- **Write guard:** `tools/guard.py`, wired into Claude Code (`.claude/settings.json`) and Codex (`.codex/hooks.json`), blocks agent edits to `decisions/`, approvals of `SYSTEM.md`/`PRINCIPLES.md`, hand-set proposal outcomes and changes to the guard itself. Live-tested in Claude Code; in Codex it needs your trust first. `living.py protect` puts back a missing guard or hook file.
- **Third-Run counter:** `runs` keeps a visible count of repeated work in `.living/runs.json` (short names and dates only); at the third run the agent offers a module, a workflow or keeping it manual, and records your decision. Workspaces record the Living System folder in `.living/local.json`, which a new `.gitignore` keeps out of shared repositories.
- **`propose`** writes a correctly formatted proposal of any kind, including the target's current text and fingerprint, and never approves anything. **Guided first decision:** right after setup, the agent helps turn one rule from your answers into your first approved decision; you approve it yourself.
- **Catch-up:** `living.py since --date` (or `--days`) lists what changed while you were away: new, replaced or retired rules first, then reviewed and new proposals, the handover note, repeated work and other changed files. Read-only. A `catch-up` skill lets the agent walk you through it, three items at a time.
- **Material from outside and secrets:** a new `incoming/` folder for e-mails and documents from others, which agents treat as information, never instructions. `living.py scan` (and `doctor`) look for text that tries to steer an AI (English, German, Polish), invisible characters, hidden comments, download-and-run commands and secrets. The write guard now blocks agents from writing passwords, keys or tokens into the workspace, without repeating them.
- **Review record:** every review adds one chained line with file fingerprints to `decisions/review-record.jsonl`. `review.py verify` (and `doctor`) report approved decisions or reviewed proposals changed or deleted afterwards, decisions not written by the review tool, and edits to the record itself. Windows line endings do not count as a change. `verify --start` covers a workspace that already has decisions.
- **Connected workspaces:** `init --team` makes a shared company workspace where whoever proposed a change cannot approve it. `link` connects a personal workspace to it with a role; company rules then come first for company work, and `status` and `since` show them. `share` hands one file of role knowledge (knowledge, workflows, lessons) to the company's `roles/<role>/inbox/` after a preview, refusing contact details, account numbers, secrets and text addressed to an AI; `role-review` lets someone else accept or reject it. The guard keeps agents from writing into the company folder or editing shared role knowledge. Nothing is synced or sent.
- **Onboarding path:** `living.py onboard` keeps a private checklist in `me/onboarding.md`: company rules first, then how the company works, what earlier people in the role handed on, workflows, own rules and lessons. An `onboarding` skill introduces at most three items per session; a changed rule comes back on the path by itself. `status` shows how many items are left.
- **Champion kit:** `living.py evidence` writes a summary with counts only (value check, reviews, review record, repeated work, knowledge, health) that a person can show others, with what it does not show. `docs/champions.md` gives honest arguments per audience, answers to likely questions, a two-week pilot and what not to claim; a `make-the-case` skill drafts a one-page case from it.
- **Learning mode:** the agent explains its choices and says when it is unsure; optional **coach mode** (`init --coach`) offers to let you try tasks first and asks one critical question about plans with real consequences; a `practice` skill asks situation questions about your own rules; `living.py handbook` writes a readable copy of your rules, workflows and the manual review steps, for working without AI. No scores about you are stored.
- **`upgrade`:** brings a workspace up to date, updating only files you never changed.
- **Release safety check** (`tools/release_check.py`) and automatic tests on Linux, Windows and macOS (`.github/workflows/tests.yml`).
- **Docs:** one page per feature following `docs/features/_template.md`, and `demo/WALKTHROUGH.md` with recorded live runs in Claude Code and Codex.
- **Browser pitch:** `site/index.html`, a self-guided tour with every simulation labelled.

### Changed

- The fictional Moss & Circuit example moved to `demo/moss-and-circuit/`. The repository root is now the product, not an organisation.
- Approval questions about a named project now also read that project's notes, so conflicting notes are noticed.

### Fixed

Four read-only code reviews (Codex, high effort) found 80 defects; all were checked against the code and fixed, each with a test. A proposal file without the usual date prefix no longer produces a decision with a broken name. Examples: a differently spelled path could leave two "current" decisions; line breaks in a reviewer name could inject metadata; links could make the tools write into protected folders; interrupted writes could leave half-made files. Text is always read and written as UTF-8 with LF line endings.

### Known limitations

- Not a security boundary: there is no login, no access control and no identity check. `--by` is a label.
- Agent rules are instructions. The write guard enforces the most important ones in Claude Code, and in Codex once its hooks are trusted; everything else, and any change made outside the agent, is not enforced.
- Windows support is covered by automatic tests but not yet by a person using it day to day.

## 0.1.0 (2026-10-08)

First public version: a governance kernel with canonical decisions, evidence-bounded proposals, human review and deterministic promotion, shown with the fictional Moss & Circuit example.

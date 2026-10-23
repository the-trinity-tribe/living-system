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
- **Optional modules:** `modules`, `add`, `remove`, with three modules: `weekly-update`, `meeting-notes`, `staged-learning`. Plans are shown before anything is written; removal keeps files you edited and never touches decisions, proposals or projects. New workspaces list the available modules in `.living/catalog.md`.
- **Workflow generator:** `new-workflow` creates a staged workflow folder in the style of Interpretable Context Methodology (see `CREDITS.md`).
- **`doctor`:** a read-only health check in plain words.
- **`status`:** what needs your attention (proposals to review, drafts, the last next step).
- **`upgrade`:** brings a workspace up to date, updating only files you never changed.
- **Release safety check** (`tools/release_check.py`) and automatic tests on Linux, Windows and macOS (`.github/workflows/tests.yml`).
- **Docs:** one page per feature following `docs/features/_template.md`, and `demo/WALKTHROUGH.md` with recorded live runs in Claude Code and Codex.
- **Browser pitch:** `site/index.html`, a self-guided tour with every simulation labelled.

### Changed

- The fictional Moss & Circuit example moved to `demo/moss-and-circuit/`. The repository root is now the product, not an organisation.
- Approval questions about a named project now also read that project's notes, so conflicting notes are noticed.

### Fixed

Three read-only code reviews (Codex, high effort) found 59 defects; all were checked against the code and fixed, each with a test. Examples: a differently spelled path could leave two "current" decisions; line breaks in a reviewer name could inject metadata; links could make the tools write into protected folders; interrupted writes could leave half-made files. Text is always read and written as UTF-8 with LF line endings.

### Known limitations

- Not a security boundary: there is no login, no access control and no identity check. `--by` is a label.
- Agent rules are instructions. An agent can still ignore them; the tools only refuse unsafe changes they are asked to make.
- Windows support is covered by automatic tests but not yet by a person using it day to day.

## 0.1.0 (2026-10-08)

First public version: a governance kernel with canonical decisions, evidence-bounded proposals, human review and deterministic promotion, shown with the fictional Moss & Circuit example.

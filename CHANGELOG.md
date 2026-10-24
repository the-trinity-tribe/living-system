# Changelog

All notable changes. Dates are when a version was prepared. Versions before 1.0 are experimental: details may change between them.

## Unreleased

### Added

- **Agency and delegation:** `living.py agency` shows who may do what in a workspace, marking what a tool enforces and what is an instruction. `living.py delegate` proposes a delegation level (observe, recommend, draft, act-with-approval, bounded) for one kind of work; it takes effect only when a human approves it and is withdrawn by retiring it. Bounded autonomy needs a scope and a review date within 90 days, and publishing, sending, spending, deleting, signing and changing rules never go above act-with-approval. AGENTS.md section 15.
- **Personal work agreement:** `me/agreement.md` (English, German, Polish) for how you want to work with AI: answers, who does what, interruptions, skills to keep, limits, sharing, explanations, when to be challenged, and what saved time is for. The agent reads it each session and never adds to it on its own; a protected-time rule keeps it from filling saved time with more work. `upgrade` adds the file to older workspaces only if none exists; nothing in `me/` is ever changed.
- **Decision escrow:** `park` takes an optional `--decide` (what needs deciding) and `--again` (a date to look again); `status` lists items whose date has come. Nothing parked is acted on.
- **Knowledge metabolism:** optional `confidence: low | medium | high` on knowledge files (doctor notes low ones); `living.py compost` moves outdated knowledge to `knowledge/archive/` with the date and reason, out of upkeep, sharing and daily use but kept as history. The `tend` skill now also offers composting, merging duplicates, and turning lessons that keep coming up into proposals.

## 0.2.0 preview (2026-10-24)

From a governance demo to a workspace you can install and grow. Released as a preview for testing and feedback; the final 0.2.0 follows after a round of hands-on testing. Release notes: [docs/releases/0.2.0-preview.1.md](docs/releases/0.2.0-preview.1.md).

### Added

#### Setting up

- **Your own workspace:** `tools/living.py init` creates a private workspace in a separate folder (never inside this repository), with nothing half-made if it fails. `INSTALL.md` lets Claude Code or Codex guide you through it with at most five questions.
- **Profiles:** `student`, `professional`, `employee`, `manager`, each with small starting files and personal goals kept apart from shared rules (`me/`, private by default for employees).
- **Language choice**, with German and Polish starter files (`core/i18n/`), and an optional **calm replies** setting for shorter, plainer agent answers. The agent's rule files stay English in every language. The value check accepts German and Polish column names and score words.
- **Shared skills** for Claude Code and Codex (`living-status`, `first-decision`, `propose-change`, `wrap-up`, `catch-up`, `practice`, `share-knowledge`, `onboarding`, `make-the-case`, `tend`, `idea-check`): one source in `core/skills/`, copied to `.claude/skills/` and `.agents/skills/` by `init` and `upgrade`, so both agents get the same short procedures.
- **Obsidian guide:** how to open a workspace as an Obsidian vault, approve drafts through the `status` property, and what not to edit by hand; workspace `.gitignore` leaves out Obsidian's window layout files.

#### Your rules and their safety

- **Decision kinds:** proposals can now add a first rule (`kind: new`), replace a rule completely (`kind: replace`) or retire one (`kind: retire`), besides adding an exception. Old decision files are never edited.
- **Decision history:** `review.py history` shows every decision, what is in force, and what amended, replaced or retired each older one.
- **`propose`** writes a correctly formatted proposal of any kind, including the target's current text and fingerprint, and never approves anything. **Guided first decision:** right after setup, the agent helps turn one rule from your answers into your first approved decision; you approve it yourself.
- **Write guard:** `tools/guard.py`, wired into Claude Code (`.claude/settings.json`) and Codex (`.codex/hooks.json`), blocks agent edits to `decisions/`, approvals of `SYSTEM.md`/`PRINCIPLES.md`, hand-set proposal outcomes and changes to the guard itself. Live-tested in Claude Code; in Codex it needs your trust first. `living.py protect` puts back a missing guard or hook file.
- **Review record:** every review adds one chained line with file fingerprints to `decisions/review-record.jsonl`. `review.py verify` (and `doctor`) report approved decisions or reviewed proposals changed or deleted afterwards, decisions not written by the review tool, and edits to the record itself. Windows line endings do not count as a change. `verify --start` covers a workspace that already has decisions.
- **Material from outside and secrets:** a new `incoming/` folder for e-mails and documents from others, which agents treat as information, never instructions. `living.py scan` (and `doctor`) look for text that tries to steer an AI (English, German, Polish), invisible characters, hidden comments, download-and-run commands and secrets. The write guard now blocks agents from writing passwords, keys or tokens into the workspace, without repeating them.
- **Working rules:** agents run a Living System command before reasoning things out (deterministic first), show a short approval screen (what, why, risk, cost in plain words, undo) before anything hard to undo or outside the workspace, stay within what was asked, and treat a new topic in the same chat as a new task. The Third-Run counter gains `improve` (keep it manual, write down better steps) and a cognitive-load exception for safe, reversible tasks.

#### Every day

- **`status`:** what needs your attention (proposals to review, drafts, the last next step), with the exact review command for each waiting proposal.
- **Handover note:** `handover/LATEST.md`, so the next session (with any agent) starts where the last one stopped.
- **Catch-up:** `living.py since --date` (or `--days`) lists what changed while you were away: new, replaced or retired rules first, then reviewed and new proposals, the handover note, repeated work and other changed files. Read-only. A `catch-up` skill lets the agent walk you through it, three items at a time.
- **Parking and tending:** `living.py park` writes an idea to `me/parked.md` in one line so work can carry on; `status` counts parked ideas. A `tend` skill goes through everything waiting one item at a time, and an `idea-check` skill helps decide whether to build something, try it by hand, park it or drop it.
- **Focus mode and a fuller handover:** `living.py focus . on|off` (AGENTS.md section 10a: no suggestions while it is on); the handover note now has a goal and one open question; `status` says when the note is older than later changes.

#### Learning and working without AI

- **Learning mode:** the agent explains its choices and says when it is unsure; optional **coach mode** (`init --coach`) offers to let you try tasks first and asks one critical question about plans with real consequences; a `practice` skill asks situation questions about your own rules; `living.py handbook` writes a readable copy of your rules, workflows and the manual review steps, for working without AI. No scores about you are stored.
- **Onboarding path:** `living.py onboard` keeps a private checklist in `me/onboarding.md`: company rules first, then how the company works, what earlier people in the role handed on, workflows, own rules and lessons. An `onboarding` skill introduces at most three items per session; a changed rule comes back on the path by itself. `status` shows how many items are left.

#### Teams

- **Connected workspaces:** `init --team` makes a shared company workspace where whoever proposed a change cannot approve it. `link` connects a personal workspace to it with a role; company rules then come first for company work, and `status` and `since` show them. `share` hands one file of role knowledge (knowledge, workflows, lessons) to the company's `roles/<role>/inbox/` after a preview, refusing contact details, account numbers, secrets and text addressed to an AI; `role-review` lets someone else accept or reject it. The guard keeps agents from writing into the company folder or editing shared role knowledge. Nothing is synced or sent.
- **Role-specific company workflows** (`Roles:` line in a workflow's `CONTEXT.md`) for the onboarding path, and a [local-first page](docs/local-first.md) on what runs offline and what is not measured.

#### Repeated work and modules

- **Third-Run counter:** `runs` keeps a visible count of repeated work in `.living/runs.json` (short names and dates only); at the third run the agent offers a module, a workflow or keeping it manual, and records your decision. Workspaces record the Living System folder in `.living/local.json`, which a new `.gitignore` keeps out of shared repositories.
- **Optional modules:** `modules`, `add`, `remove`, with ten modules (listed in the README). Plans are shown before anything is written; removal keeps files you edited and never touches decisions, proposals or projects. New workspaces list the available modules in `.living/catalog.md`.
- **Workflow generator:** `new-workflow` creates a staged workflow folder in the style of Interpretable Context Methodology (see `CREDITS.md`).
- **Careful-run module:** bigger or riskier work in six steps (frame, plan, make, check in a fresh session, verify with tools, hand back), one run card per run with scope, risk, who makes and who checks, how to undo and how to verify; high-risk runs need your yes on the plan. `living.py checkpoint` records fingerprints of the card's files when pausing and lists what changed before resuming.
- **Four more modules:** `work-audit` (map the work, find friction, drop before automating, test one small change, measure), `research-review` (dated sources, checked claims, conflicts and gaps), `client-intake` (need, unknowns, next step, client codes instead of contact details) and `content-prep` (brief, draft, fact and tone check, you publish).

#### Upkeep

- **`doctor`:** a read-only health check in plain words.
- **Knowledge upkeep in `doctor`:** references in workflows, knowledge and role knowledge to replaced, retired or missing decisions (with the rule that applies now), likely duplicate knowledge files, a flat `knowledge/` folder that needs topic drawers, and an `AGENTS.md` grown far beyond its installed length. AGENTS.md says when to make a drawer.
- **Health files and a menu:** `doctor --out` saves the report as Markdown outside the workspace; `export-check` confirms a backup zip is a complete workspace; `living.py` with no command (or `menu`) shows the everyday commands in plain words.
- **Export:** `living.py export` packs a workspace into one zip (without machine-specific files); `upgrade` on a restored copy records the new computer's Living System folder.
- **`upgrade`:** brings a workspace up to date, updating only files you never changed.

#### Showing value

- **Value check:** a 10-minute before/after test you run yourself, and `value-score` to count the results.
- **Champion kit:** `living.py evidence` writes a summary with counts only (value check, reviews, review record, repeated work, knowledge, health) that a person can show others, with what it does not show. `docs/champions.md` gives honest arguments per audience, answers to likely questions, a two-week pilot and what not to claim; a `make-the-case` skill drafts a one-page case from it.

#### Project

- **Release safety check** (`tools/release_check.py`) and automatic tests on Linux, Windows and macOS (`.github/workflows/tests.yml`).
- **Docs:** one page per feature following `docs/features/_template.md`, and `demo/WALKTHROUGH.md` with recorded live runs in Claude Code and Codex.
- **For testers and contributors:** [TESTING.md](TESTING.md) (a 30-minute path), feedback, bug and idea forms, a pull request checklist, a fuller [CONTRIBUTING.md](CONTRIBUTING.md), a [code of conduct](CODE_OF_CONDUCT.md), a [roadmap](docs/roadmap.md) with every deferral and rejection explained, and an [evaluation](docs/evaluations/laya/README.md) of a small local decision model (not adopted).
- **Browser pitch:** `site/index.html`, a self-guided tour with every simulation labelled.

### Changed

- The fictional Moss & Circuit example moved to `demo/moss-and-circuit/`. The repository root is now the product, not an organisation.
- Approval questions about a named project now also read that project's notes, so conflicting notes are noticed.

### Fixed

Six read-only code reviews (Codex, high effort) found 124 defects; all were checked against the code and fixed, each with a test. A proposal file without the usual date prefix no longer produces a decision with a broken name. Examples: a differently spelled path could leave two "current" decisions; line breaks in a reviewer name could inject metadata; links could make the tools write into protected folders; interrupted writes could leave half-made files. Text is always read and written as UTF-8 with LF line endings.

### Known limitations

- Not a security boundary: there is no login, no access control and no identity check. `--by` is a label.
- Agent rules are instructions. The write guard enforces the most important ones in Claude Code, and in Codex once its hooks are trusted; everything else, and any change made outside the agent, is not enforced.
- Windows support is covered by automatic tests but not yet by a person using it day to day.
- Skills, coaching, onboarding, tend and focus mode are instructions to the agent; they are tested in recorded sessions, not by the automatic tests. This preview asks testers to try them.
- German and Polish starter files have not had a native-speaker review yet.

## 0.1.0 (2026-10-08)

First public version: a governance kernel with canonical decisions, evidence-bounded proposals, human review and deterministic promotion, shown with the fictional Moss & Circuit example.

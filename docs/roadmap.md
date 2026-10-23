# Roadmap and capability review

Status: EXPERIMENTAL. Version: 0.2.0. Reviewed on 2026-10-24.

Which capabilities Living System has, which it will get, and which it deliberately will not. Coverage was checked against the code and tests, not against descriptions. "Unverified" means the behaviour is an agent instruction that has not yet been tested in a live session.

Decisions: **Keep** (already right), **Core** (everyone gets it), **Module** (optional), **Enhancement** (small addition to something that exists), **Defer** (not now, with a condition), **Reject** (with a reason).

## Order of work

| # | Step | Areas | What | Size |
| --- | --- | --- | --- | --- |
| 1 | Agent rules batch | C, E, F, I, B | General approval screen; deterministic first; topic switch means context switch; cognitive-load exception; scope expansion needs a yes. | Small |
| 2 | Parking and tend | G, A, N | `me/parked.md` and 'park this'; `tend` skill; `idea-check` skill. | Small |
| 3 | Focus setting and capsule | G, F | `focus` setting; handover goal and open question; stale handover note in status. | Small |
| 4 | Knowledge upkeep | A, K, I | Drawer rule; duplicate knowledge; stale references in workflows and knowledge; instruction growth; `improve` choice. | Small to medium |
| 5 | Careful-run module | B, E | Run card, profiles, risk rule, checkpoints, `run-check`. | Medium |
| 6 | Health files | L, C | `doctor --out`, `export --check`, menu. | Small |
| 7 | New modules | M, P | `work-audit`, `research-review`, `client-intake`, `content-prep`. | Medium (content) |
| 8 | Role-specific workflows | H | Workflows name their roles; onboarding filters. | Small |
| 9 | Local-first page | O | What runs offline, what needs an agent, what is not measured. | Small |
| 10 | Decision model benchmark | D | Only with your permission to download: Laya on a labelled set of real requests vs keyword signals. | Medium, optional |

## Coverage and decisions

### A. Knowledge governance and lifecycle

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Canonical decisions vs working context vs unreviewed evidence | Implemented | Keep | Authority order in AGENTS.md section 2; proposals are never truth; `incoming/` is information only. |
| Staging for decisions, knowledge and lessons | Implemented | Keep | `proposals/`, `knowledge-inbox` module, `staged-learning` module, `roles/<role>/inbox/`. |
| Staging for tasks | Missing | Reject | Living System is not a task manager; people already have one. Reconsider if several users ask for task hand-offs inside the workspace. |
| Human review, promotion, rejection, deferral | Implemented | Keep | `review.py review` (four proposal kinds), `role-review`; the guard blocks hand-set outcomes. |
| Knowledge drawers by domain, created only when justified | Partial | Enhancement | Subfolders work, but nothing says when to make one. Add a rule (a drawer once about five files share a topic) and a doctor note when `knowledge/` grows flat. |
| Freshness, source verification, expiry warnings | Implemented | Keep | `last_verified`, doctor and status re-check reminders after 90 days, sources required by `knowledge-inbox`. |
| Supersession and retirement of decisions | Implemented | Keep | `replace` and `retire` proposals; history; review record. |
| Deduplication and consolidation of knowledge | Missing | Enhancement | Doctor notes knowledge files with the same title or identical text, so the human can merge them. |
| Active lessons with a size limit | Implemented | Keep | `staged-learning`: at most 15 active lessons, doctor warns. |
| 'Tend': one calm maintenance pass, item by item | Missing | Core | A `tend` skill that walks through everything waiting (proposals, inboxes, stale knowledge, due runs, parked ideas) one item at a time, using `status`. |
| Stale routing instructions and references | Partial | Enhancement | `check` covers routing paths and superseded decisions named in `projects/`. Extend to workflows and knowledge files. |
| Decision provenance and history | Implemented | Keep | `source_proposal`, `supersedes`, `review.py history`, `decisions/review-record.jsonl`. |

### B. Careful runs (bounded task execution)

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Frame, plan, make, check, verify, hand back | Partial | Module | `second-check` covers make, check, decide. Missing: framing, a plan with scope and rollback, deterministic verification and the hand-back. Build one optional `careful-run` module rather than a parallel engine. |
| Run card: scope, permissions, agent or model, expected output, rollback | Missing | Module | Part of `careful-run`, a single Markdown file per run. |
| Task profiles (code, website, content, research, operations, general) | Missing | Module | Short profile checklists inside `careful-run/references/`, not separate engines. |
| Risk and complexity classification | Missing | Module | Deterministic: anything that publishes, spends, deletes, messages people or changes rules is high risk and needs the human at the plan stage. |
| Maker/checker separation, fresh-session review, other provider | Implemented | Keep | `second-check` (Unverified live). `careful-run` reuses the same rule. |
| Bounded correction loops | Implemented | Keep | `second-check`: at most two rounds without the human's yes. |
| Pause, resume, cancel; checkpoints; revalidate files before resuming | Missing | Module | Run card records the stage and file fingerprints; `living.py run-check` says what changed since the checkpoint before work continues. |
| Durable hand-offs | Implemented | Keep | Handover note, catch-up; the run card is a second, task-scoped hand-off. |
| Feedback on routes that worked or failed | Missing | Defer | Needs real runs first. Reconsider after ten or more recorded runs; then a short 'what worked' line per run card is enough. |
| Explicit authorisation before expanding scope | Unverified | Core | Say it once in AGENTS.md: work beyond the run card or the request needs the human's yes. |

### C. Operational governance

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Read-only status | Implemented | Keep | `status`, `since`, `doctor`. |
| Preflight checks | Implemented | Keep | `doctor`, `review.py check`, `verify`, plans before every `--apply`. |
| Approval screens with scope, risk, reason, cost, rollback | Partial | Core | Only setup has one. Add one general approval-screen rule for any irreversible or outward-facing step; cost is stated in plain words (for example 'one extra fresh session'), never as an invented number. |
| Human-readable operational log | Partial | Defer | The review record, runs, handover and git history already cover what matters. A separate action log grows fast and repeats git. Reconsider if a team needs an audit trail beyond git. |
| Bounded repair and failure triage | Implemented | Keep | `protect`, `upgrade`, doctor messages that say how to fix. |
| Deterministic checks before AI analysis | Partial | Core | Tools exist; add the rule: run the tool first, ask the AI only for what a tool cannot decide. |
| End-of-session wrap-up | Implemented | Keep | `wrap-up` skill, handover note. |
| Safe practice sandbox | Implemented | Keep | The fictional demo workspace and `demo/WALKTHROUGH.md`. |
| Recovery procedures | Implemented | Keep | `export`, restore by unzip and `upgrade`, `protect`, git. |
| Simple human-facing menu | Missing | Enhancement | `living.py` with no command shows a short menu of everyday tasks in plain words. |

### D. Lightweight decision models (Laya, Jev)

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Typed, probability-based decisions for classification and routing | Missing | Defer | Facts checked: Laya (Apache-2.0, 322-421M parameters, ~650-800 MB, needs PyTorch) is near chance on typed decisions without fine-tuning (0.362 base vs 0.766 fine-tuned) and ships over-confident. Jev is hosted, proprietary, in early access. Living System's own decisions are deterministic today and need no model. |
| Local vs hosted inference; CPU suitability | Missing | Defer | Laya runs on CPU at a reported 193-464 ms per question; Jev sends data to a third party. Both would break the standard-library-only, offline core. |
| Replaceable decision-model adapter with confidence thresholds and fallback | Missing | Defer | Only worth it with a proven use. Candidate: suggesting a module from a request. Reconsider after a benchmark on a labelled set of real requests (needs your permission to download the model) shows clear gains over keyword signals, with abstention below a threshold and the rule-based path as fallback. |
| Never bypass human approval or governance | Implemented | Keep | No component can approve; any future adapter may only suggest. |

### E. Model and task routing

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Scripts for deterministic tasks | Implemented | Keep | Every counting, checking and writing step is a tool command. |
| Choose agent or model by complexity and risk; minimum capability for high-risk work | Missing | Module | Written into the `careful-run` card: who makes, who checks, and a stronger checker for high-risk runs. No routing engine: Claude Code and Codex already pick models. |
| Bounded context per task | Implemented | Keep | Context routing, stage-local `CONTEXT.md`. |
| Recording routing successes and failures | Missing | Defer | Same as B: after real runs. |
| Configurable provider catalogs; billing boundaries | Missing | Reject | Living System never calls a model or an API, so it has no providers to configure and no bill. Reconsider only if a model adapter (D) is ever added. |

### F. Context routing and session continuity

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Stable entry points, progressive disclosure, stage-local context | Implemented | Keep | `AGENTS.md`, `CLAUDE.md`, `CONTEXT-ROUTING.md`, ICM stages, skills. |
| Context capsule: goal, changes, open question, next action | Partial | Enhancement | Handover has done, open and next step. Add 'goal' and 'open question' to the template and the wrap-up skill. |
| Routing by actual task, not window; a topic switch is a context switch | Missing | Core | AGENTS.md rule: when the topic changes in one chat, write a short capsule for the old task and re-route for the new one. |
| Stale-context detection | Partial | Enhancement | Status says when the handover note is older than the latest changes in the workspace. |
| Cold-open tests | Implemented | Keep | Value check, recorded runs in the walkthrough (manual by design). |
| Vendor-exit test | Partial | Keep | Same files work in Claude Code and Codex; `handbook` works without any AI. A scripted drill adds little. |

### G. Human sustainability

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Adjustable response density and guidance | Implemented | Keep | `calm_replies`, coach mode (Unverified live). |
| Parking ideas without switching task | Missing | Core | 'Park this': the agent adds one line to `me/parked.md` and carries on; status and tend list them later. |
| User-controlled focus protection | Missing | Enhancement | Opt-in `focus` setting: no suggestions (modules, sharing, coaching offers, catch-up) until switched off. Reversible in one sentence. |
| Context restoration after interruptions | Implemented | Keep | Handover note, catch-up, capsule (F). |
| Clear next action | Implemented | Keep | Status, handover next step, calm replies. |
| Friction tracking | Partial | Keep | The value-check log is the place; no extra mechanism. |
| Workload check-ins, interruptibility states, reminders | Missing | Reject | Check-ins invite psychological inference, and reminders need a background process. Focus mode covers the useful part. Reconsider check-ins only as a user-written prompt in their own calendar. |

### H. Employee augmentation

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Organisation, role and person layers; shared plus private workspaces | Implemented | Keep | `init --team`, `link`, `roles/<role>/`, `me/`. |
| Knowledge continuity across role changes | Implemented | Keep | `share`, `role-review`, onboarding reads role knowledge. |
| Progressive onboarding | Implemented | Keep | `onboard`, `onboarding` skill (Unverified live). |
| Learning and coaching, guided practice, explaining how | Implemented | Keep | AGENTS.md section 13, `practice` skill, coach mode (Unverified live). |
| Working without AI | Implemented | Keep | `handbook`. |
| Role-specific workflows | Partial | Enhancement | Company workflows reach every role. Let a workflow name its roles, so onboarding shows each person only theirs. |

### I. Automation maturity

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Third-Run Rule, counting, remembered decisions, module suggestions | Implemented | Keep | `runs`, catalog, AGENTS.md section 11. |
| 'Improve' as a fourth choice | Missing | Enhancement | Add `improve` (keep it manual, but write down better steps) next to automate, manual and later. |
| Preventing repeated unwanted recommendations | Implemented | Keep | Decisions are remembered; 'later' asks again only after more runs. |
| Cognitive-load exception for safe, deterministic, reversible tasks | Missing | Core | AGENTS.md: such a task may be automated before the third run if the human says it costs them a lot; approvals for publishing, spending, deleting, messaging and rule changes stay. |

### J. Modules and staged workflows

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Installable, removable, upgradable modules with plans | Implemented | Keep | `add`, `remove`, `upgrade`, hash tracking. |
| Generated staged folders with stage CONTEXT.md, inputs, outputs, checkpoints | Implemented | Keep | `new-workflow`. |
| Module recommendations from recurring needs | Implemented | Keep | Signals in the catalog, Third-Run Rule. |
| Thin Claude Code and Codex adapters | Implemented | Keep | `CLAUDE.md` points to `AGENTS.md`; shared skills. |
| Dependency declarations between modules | Missing | Defer | No module needs another yet; `careful-run` stays self-contained. Reconsider when two modules must be installed together. |
| Kinds: knowledge, skill, workflow, capability | Implemented | Keep | `kind` in `module.json`. |

### K. Continuous improvement

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Capturing failures as reusable lessons, human adoption | Implemented | Keep | `staged-learning`. |
| No self-modifying safety rules | Implemented | Keep | The guard protects itself and the review tool; AGENTS.md is product-owned. |
| Staged suggestions to change instructions | Partial | Keep | Lessons are the staged path; changes to the product's AGENTS.md go through the project itself. |
| Instruction and knowledge bloat | Partial | Enhancement | Doctor notes when your own additions make AGENTS.md or CONTEXT-ROUTING.md much longer than installed. |
| Duplicated or obsolete instructions; tracking failed approaches | Missing | Defer | Hard to detect reliably without a model; lessons cover failed approaches. Reconsider with real workspaces to test against. |

### L. System health and resilience

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Expanded diagnostics: routing, proposals, freshness, lessons, hooks, privacy, secrets | Implemented | Keep | `doctor` (guard, scan, verify, link checks). |
| Export and recovery validation | Partial | Enhancement | `export --check <zip>` opens a zip and confirms it is a complete workspace. |
| Readable health report file | Missing | Enhancement | `doctor --out report.md`, outside the workspace, plain Markdown. |
| Regression tests | Implemented | Keep | Over 320 tests on Linux, Windows and macOS. |

### M. Work audit before adding AI

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Map work, find bottlenecks, separate judgement, eliminate, augment, automate, experiment, measure | Missing | Module | An optional `work-audit` staged workflow with a stop for the human at each step and no return-on-investment numbers unless measured. |

### N. Deciding what not to build

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Structured idea check: frequency, alternatives, benefit, maintenance, privacy, load, smallest version, evidence | Missing | Core | An `idea-check` skill that ends in build, try smallest, park or drop; parked ideas go to `me/parked.md`. |

### O. Local-first and resource use

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Readable canonical files, offline core, deterministic tools, minimal runtime, portable backups | Implemented | Keep | Plain Markdown and JSON, Python standard library, no network, `export`. |
| Optional local models | Missing | Defer | See D. |
| Avoiding repeated inference | Partial | Keep | Tools answer status questions without an AI; routing keeps context small. |
| Resource measurement | Missing | Reject | Living System cannot measure the agents' energy use, and estimates would be speculative claims. A short page states what it does and does not do. |

### P. Business workflows and docs

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Meeting-to-action, weekly update, second check, knowledge capture | Implemented | Keep | Existing modules. |
| Research and evidence review | Missing | Module | `research-review`: question, sources with dates, claims checked against sources, open gaps. |
| Client intake | Missing | Module | `client-intake`: what the client needs, constraints, what is unknown, proposal for next step; contact details stay out of shared files. |
| Content preparation | Missing | Module | `content-prep`: brief, draft, fact and tone check, human publishes. |
| Marketing planning | Missing | Defer | Overlaps content preparation; reconsider after `content-prep` is used. |
| Recruitment and role onboarding | Partial | Defer | Role onboarding exists (`onboard`). Recruitment handles candidates' personal data; too risky for a template now. |
| Controlled external integrations | Missing | Defer | Needs connectors and their security review; agents' own connectors already exist. |
| Clean install, conversational setup, demo isolation, feature docs, labels in the pitch | Implemented | Keep | Tested; the pitch waits for the final state. |

## Not now, and not at all

Every **Defer** and **Reject** above, in one list.

- **Reject** (A) Staging for tasks: Living System is not a task manager; people already have one. Reconsider if several users ask for task hand-offs inside the workspace.
- **Defer** (B) Feedback on routes that worked or failed: Needs real runs first. Reconsider after ten or more recorded runs; then a short 'what worked' line per run card is enough.
- **Defer** (C) Human-readable operational log: The review record, runs, handover and git history already cover what matters. A separate action log grows fast and repeats git. Reconsider if a team needs an audit trail beyond git.
- **Defer** (D) Typed, probability-based decisions for classification and routing: Facts checked: Laya (Apache-2.0, 322-421M parameters, ~650-800 MB, needs PyTorch) is near chance on typed decisions without fine-tuning (0.362 base vs 0.766 fine-tuned) and ships over-confident. Jev is hosted, proprietary, in early access. Living System's own decisions are deterministic today and need no model.
- **Defer** (D) Local vs hosted inference; CPU suitability: Laya runs on CPU at a reported 193-464 ms per question; Jev sends data to a third party. Both would break the standard-library-only, offline core.
- **Defer** (D) Replaceable decision-model adapter with confidence thresholds and fallback: Only worth it with a proven use. Candidate: suggesting a module from a request. Reconsider after a benchmark on a labelled set of real requests (needs your permission to download the model) shows clear gains over keyword signals, with abstention below a threshold and the rule-based path as fallback.
- **Defer** (E) Recording routing successes and failures: Same as B: after real runs.
- **Reject** (E) Configurable provider catalogs; billing boundaries: Living System never calls a model or an API, so it has no providers to configure and no bill. Reconsider only if a model adapter (D) is ever added.
- **Reject** (G) Workload check-ins, interruptibility states, reminders: Check-ins invite psychological inference, and reminders need a background process. Focus mode covers the useful part. Reconsider check-ins only as a user-written prompt in their own calendar.
- **Defer** (J) Dependency declarations between modules: No module needs another yet; `careful-run` stays self-contained. Reconsider when two modules must be installed together.
- **Defer** (K) Duplicated or obsolete instructions; tracking failed approaches: Hard to detect reliably without a model; lessons cover failed approaches. Reconsider with real workspaces to test against.
- **Defer** (O) Optional local models: See D.
- **Reject** (O) Resource measurement: Living System cannot measure the agents' energy use, and estimates would be speculative claims. A short page states what it does and does not do.
- **Defer** (P) Marketing planning: Overlaps content preparation; reconsider after `content-prep` is used.
- **Defer** (P) Recruitment and role onboarding: Role onboarding exists (`onboard`). Recruitment handles candidates' personal data; too risky for a template now.
- **Defer** (P) Controlled external integrations: Needs connectors and their security review; agents' own connectors already exist.

## Risks to watch

- Sunday's test now covers more: every increment adds checklist steps, and agent behaviour (skills, coach, focus) is only verified live.
- Instruction growth: each rule makes AGENTS.md longer. Keep each rule to a few lines and prefer skills for procedures.
- Content modules can look like promises. Each says what it does not do.
- Decision models (D) stay out of the core unless a benchmark you approve shows a clear gain.

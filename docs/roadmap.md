# Roadmap and capability review

Status: EXPERIMENTAL. Version: 0.2.0. Reviewed on 2026-10-24.

Which capabilities Living System has, which it will get, and which it deliberately will not. Coverage was checked against the code and tests, not against descriptions. "Unverified" means the behaviour is an agent instruction that has not yet been tested in a live session.

Decisions: **Keep** (already right), **Core** (everyone gets it), **Module** (optional), **Enhancement** (small addition to something that exists), **Defer** (not now, with a condition), **Reject** (with a reason).

## Order of work

All ten steps were done on 2026-10-24: steps 1 to 9 built with tests, step 10 an evaluation that ended in 'not adopted'.

| # | Step | Areas | What | Size |
| --- | --- | --- | --- | --- |
| 1 | Agent rules batch | C, E, F, I, B | General approval screen; deterministic first; topic switch means context switch; cognitive-load exception; scope expansion needs a yes. | Small |
| 2 | Parking and tend | G, A, N | `me/parked.md` and 'park this'; `tend` skill; `idea-check` skill. | Small |
| 3 | Focus setting and capsule | G, F | `focus` setting; handover goal and open question; stale handover note in status. | Small |
| 4 | Knowledge upkeep | A, K, I | Drawer rule; duplicate knowledge; stale references in workflows and knowledge; instruction growth; `improve` choice. | Small to medium |
| 5 | Careful-run module | B, E | Run card, profiles, risk rule, checkpoints, `checkpoint`. | Medium |
| 6 | Health files | L, C | `doctor --out`, `export-check`, menu. | Small |
| 7 | New modules | M, P | `work-audit`, `research-review`, `client-intake`, `content-prep`. | Medium (content) |
| 8 | Role-specific workflows | H | Workflows name their roles; onboarding filters. | Small |
| 9 | Local-first page | O | What runs offline, what needs an agent, what is not measured. | Small |
| 10 | Decision model benchmark | D | Done 2026-10-24: Laya vs keyword signals on 72 labelled requests; not adopted (docs/evaluations/laya). | Done |

## Coverage and decisions

### A. Knowledge governance and lifecycle

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Canonical decisions vs working context vs unreviewed evidence | Implemented | Keep | Authority order in AGENTS.md section 2; proposals are never truth; `incoming/` is information only. |
| Staging for decisions, knowledge and lessons | Implemented | Keep | `proposals/`, `knowledge-inbox` module, `staged-learning` module, `roles/<role>/inbox/`. |
| Staging for tasks | Missing | Reject | Living System is not a task manager; people already have one. Reconsider if several users ask for task hand-offs inside the workspace. |
| Human review, promotion, rejection, deferral | Implemented | Keep | `review.py review` (four proposal kinds), `role-review`; the guard blocks hand-set outcomes. |
| Knowledge drawers by domain, created only when justified | Unverified | Enhancement | Built (agent behaviour, not yet live-tested): Drawer rule in AGENTS.md; doctor notes a flat folder of more than 15 files. |
| Freshness, source verification, expiry warnings | Implemented | Keep | `last_verified`, doctor and status re-check reminders after 90 days, sources required by `knowledge-inbox`. |
| Supersession and retirement of decisions | Implemented | Keep | `replace` and `retire` proposals; history; review record. |
| Deduplication and consolidation of knowledge | Implemented | Enhancement | Built: Doctor notes knowledge files with the same title or identical text. |
| Active lessons with a size limit | Implemented | Keep | `staged-learning`: at most 20 active lessons, doctor warns. |
| 'Tend': one calm maintenance pass, item by item | Unverified | Core | Built (agent behaviour, not yet live-tested): `tend` skill over `status` and `park`. |
| Stale routing instructions and references | Implemented | Enhancement | Built: Doctor notes references in workflows, knowledge and role knowledge to replaced, retired or missing decisions. |
| Decision provenance and history | Implemented | Keep | `source_proposal`, `supersedes`, `review.py history`, `decisions/review-record.jsonl`. |

### B. Careful runs (bounded task execution)

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Frame, plan, make, check, verify, hand back | Implemented | Module | Built: `careful-run` module (six stages). |
| Run card: scope, permissions, agent or model, expected output, rollback | Implemented | Module | Built: `careful-run/references/run-card.md`. |
| Task profiles (code, website, content, research, operations, general) | Implemented | Module | Built: `careful-run/references/profiles.md`. |
| Risk and complexity classification | Implemented | Module | Built: Deterministic risk list in `careful-run/CONTEXT.md`; high risk needs your yes on the plan. |
| Maker/checker separation, fresh-session review, other provider | Implemented | Keep | `second-check` (Unverified live). `careful-run` reuses the same rule. |
| Bounded correction loops | Implemented | Keep | `second-check`: at most two rounds without the human's yes. |
| Pause, resume, cancel; checkpoints; revalidate files before resuming | Implemented | Module | Built: `living.py checkpoint` records and compares file fingerprints. |
| Durable hand-offs | Implemented | Keep | Handover note, catch-up; the run card is a second, task-scoped hand-off. |
| Feedback on routes that worked or failed | Missing | Defer | Needs real runs first. Reconsider after ten or more recorded runs; then a short 'what worked' line per run card is enough. |
| Explicit authorisation before expanding scope | Unverified | Core | Built (agent behaviour, not yet live-tested): AGENTS.md 'Stay in scope'; run card 'Scope changes'. |

### C. Operational governance

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Read-only status | Implemented | Keep | `status`, `since`, `doctor`. |
| Preflight checks | Implemented | Keep | `doctor`, `review.py check`, `verify`, plans before every `--apply`. |
| Approval screens with scope, risk, reason, cost, rollback | Unverified | Core | Built (agent behaviour, not yet live-tested): AGENTS.md 'Approval screen' rule. |
| Human-readable operational log | Partial | Defer | The review record, runs, handover and git history already cover what matters. A separate action log grows fast and repeats git. Reconsider if a team needs an audit trail beyond git. |
| Bounded repair and failure triage | Implemented | Keep | `protect`, `upgrade`, doctor messages that say how to fix. |
| Deterministic checks before AI analysis | Unverified | Core | Built (agent behaviour, not yet live-tested): AGENTS.md 'Deterministic first' rule. |
| End-of-session wrap-up | Implemented | Keep | `wrap-up` skill, handover note. |
| Safe practice sandbox | Implemented | Keep | The fictional demo workspace and `demo/WALKTHROUGH.md`. |
| Recovery procedures | Implemented | Keep | `export`, restore by unzip and `upgrade`, `protect`, git. |
| Simple human-facing menu | Implemented | Enhancement | Built: `living.py` with no command, or `living.py menu`. |

### D. Lightweight decision models (Laya, Jev)

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Typed, probability-based decisions for classification and routing | Experimental | Defer | Benchmarked 2026-10-24 (docs/evaluations/laya): Laya's English model picked the right module 72% of the time against 50% for keyword signals, but missed 'approve my pending proposal' and 'change the rule' on risk. Agents already make suggestions in context. Not adopted. |
| Local vs hosted inference; CPU suitability | Experimental | Defer | Measured on CPU: about 2 s and 2.8 GB of memory per request with three questions, 2.4 GB to download and install. Jev not tested: hosted and proprietary, requests would leave the computer. |
| Replaceable decision-model adapter with confidence thresholds and fallback | Missing | Defer | Reconsider only if suggestions are needed without an agent, a few hundred real labelled requests exist for fine-tuning, and the adapter can stay outside the standard-library core. It would only ever suggest, never decide risk or approve. |
| Never bypass human approval or governance | Implemented | Keep | No component can approve; any future adapter may only suggest. |

### E. Model and task routing

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Scripts for deterministic tasks | Implemented | Keep | Every counting, checking and writing step is a tool command. |
| Choose agent or model by complexity and risk; minimum capability for high-risk work | Unverified | Module | Built (agent behaviour, not yet live-tested): Run card 'Who does what'; high risk needs a checker at least as capable. |
| Bounded context per task | Implemented | Keep | Context routing, stage-local `CONTEXT.md`. |
| Recording routing successes and failures | Missing | Defer | Same as B: after real runs. |
| Configurable provider catalogs; billing boundaries | Missing | Reject | Living System never calls a model or an API, so it has no providers to configure and no bill. Reconsider only if a model adapter (D) is ever added. |

### F. Context routing and session continuity

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Stable entry points, progressive disclosure, stage-local context | Implemented | Keep | `AGENTS.md`, `CLAUDE.md`, `CONTEXT-ROUTING.md`, ICM stages, skills. |
| Context capsule: goal, changes, open question, next action | Unverified | Enhancement | Built (agent behaviour, not yet live-tested): Handover templates (en, de, pl) and wrap-up skill. |
| Routing by actual task, not window; a topic switch is a context switch | Unverified | Core | Built (agent behaviour, not yet live-tested): AGENTS.md section 9. |
| Stale-context detection | Implemented | Enhancement | Built: `status` notes a handover older than later changes. |
| Cold-open tests | Implemented | Keep | Value check, recorded runs in the walkthrough (manual by design). |
| Vendor-exit test | Partial | Keep | Same files work in Claude Code and Codex; `handbook` works without any AI. A scripted drill adds little. |

### G. Human sustainability

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Adjustable response density and guidance | Implemented | Keep | `calm_replies`, coach mode (Unverified live). |
| Parking ideas without switching task | Implemented | Core | Built: `living.py park`; `status` counts parked ideas. |
| User-controlled focus protection | Unverified | Enhancement | Built (agent behaviour, not yet live-tested): `living.py focus on|off`; AGENTS.md section 10a. |
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
| Role-specific workflows | Implemented | Enhancement | Built: `Roles:` line in a company workflow's CONTEXT.md filters onboarding. |

### I. Automation maturity

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Third-Run Rule, counting, remembered decisions, module suggestions | Implemented | Keep | `runs`, catalog, AGENTS.md section 11. |
| 'Improve' as a fourth choice | Implemented | Enhancement | Built: `runs --decide <name> improve`. |
| Preventing repeated unwanted recommendations | Implemented | Keep | Decisions are remembered; 'later' asks again only after more runs. |
| Cognitive-load exception for safe, deterministic, reversible tasks | Unverified | Core | Built (agent behaviour, not yet live-tested): AGENTS.md section 11. |

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
| Instruction and knowledge bloat | Unverified | Enhancement | Built (agent behaviour, not yet live-tested): Doctor notes AGENTS.md growth of more than 60 lines. |
| Duplicated or obsolete instructions; tracking failed approaches | Missing | Defer | Hard to detect reliably without a model; lessons cover failed approaches. Reconsider with real workspaces to test against. |

### L. System health and resilience

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Expanded diagnostics: routing, proposals, freshness, lessons, hooks, privacy, secrets | Implemented | Keep | `doctor` (guard, scan, verify, link checks). |
| Export and recovery validation | Implemented | Enhancement | Built: `living.py export-check`. |
| Readable health report file | Implemented | Enhancement | Built: `doctor --out`. |
| Regression tests | Implemented | Keep | Over 320 tests on Linux, Windows and macOS. |

### M. Work audit before adding AI

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Map work, find bottlenecks, separate judgement, eliminate, augment, automate, experiment, measure | Implemented | Module | Built: `work-audit` module. |

### N. Deciding what not to build

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Structured idea check: frequency, alternatives, benefit, maintenance, privacy, load, smallest version, evidence | Unverified | Core | Built (agent behaviour, not yet live-tested): `idea-check` skill. |

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
| Research and evidence review | Implemented | Module | Built: `research-review` module. |
| Client intake | Implemented | Module | Built: `client-intake` module. |
| Content preparation | Implemented | Module | Built: `content-prep` module. |
| Marketing planning | Missing | Defer | Overlaps content preparation; reconsider after `content-prep` is used. |
| Recruitment and role onboarding | Partial | Defer | Role onboarding exists (`onboard`). Recruitment handles candidates' personal data; too risky for a template now. |
| Controlled external integrations | Missing | Defer | Needs connectors and their security review; agents' own connectors already exist. |
| Clean install, conversational setup, demo isolation, feature docs, labels in the pitch | Implemented | Keep | Tested; the pitch waits for the final state. |

## Second review: product maturity (2026-10-24)

A second set of ideas, checked the same way after the 0.2.0 preview was published.

| # | Step | Areas | What | Size |
| --- | --- | --- | --- | --- |
| 1 | Agency and delegation | A, B | `agency`, `delegate`, AGENTS.md section on delegation levels. | Medium |
| 2 | Personal work agreement | D, E, F | `me/agreement.md` in three languages, protected time rule. | Small |
| 3 | Escrow and gardener | I, C | `park` fields and due dates; tend offers lessons as proposals. | Small |
| 4 | Knowledge metabolism | C | Confidence field, `compost`. | Small |
| 5 | Experiments and ethics | H, P, G | `small-experiment` module, four dimensions in evidence, `docs/ethics.md`. | Medium |
| 6 | Atlas, perspectives, sharing, run states | N, O, M, J | `atlas`, `perspectives` skill, `share --withdraw`, seven run states in careful-run. | Medium |

### 2A. Agency protocol

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Who may read, propose, execute, approve and verify, in one place | Partial | Core | Spread over AGENTS.md, the guard and the team rule. Add `living.py agency`: one read-only view of who may do what in this workspace, marking each line as enforced by a tool or an instruction only. |
| Task-specific authority granted and withdrawn | Missing | Core | Delegations become ordinary approved decisions (made with `living.py delegate`, withdrawn by retiring them), so they get review, history and the review record for free. |
| Uncertainty, provenance, reversibility, escalation | Implemented | Keep | AGENTS.md sections 4-7, approval screen, review record, careful-run risk rule. |

### 2B. Progressive delegation (trust ladder)

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Levels: observe, recommend, draft, act with approval, bounded autonomy | Missing | Core | Five named levels per kind of work, in delegation decisions. Default when nothing is delegated: draft and ask. |
| Evidence-based promotion, limits, rollback | Missing | Core | A delegation proposal must name its evidence and, for bounded autonomy, a scope and a review date. Publishing, spending, deleting, messaging people and changing rules can never be delegated beyond 'act with approval'. Retire the decision to withdraw it. |
| Technically enforced autonomy limits | Missing | Reject | Delegations are instructions; the guard's blocks stay as they are and no delegation lifts them. Claiming enforcement would be false. Reconsider only with a mechanism the tools can actually check. |

### 2C. Knowledge metabolism

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Signals to knowledge with human gates | Implemented | Keep | `incoming/`, `knowledge-inbox`, `staged-learning`, proposals. |
| Confidence and evidence quality | Missing | Enhancement | Optional `confidence: low | medium | high` in knowledge front matter; doctor notes low-confidence files that are old. |
| Aging and re-verification; dedup | Implemented | Keep | `last_verified`, doctor and status reminders, duplicate notes. |
| Purposeful forgetting that keeps history | Missing | Enhancement | `living.py compost` moves a knowledge file to `knowledge/archive/` with the date and reason (plan first); archived files leave routing and upkeep but stay readable. |
| Lessons graduating into rules; a gardener that only proposes | Partial | Enhancement | Lessons that would change a rule already become proposals. Extend the `tend` skill: lessons used often are offered as proposals; old or doubtful knowledge is offered for re-check or composting. |

### 2D. Personal work agreement

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| A user-owned agreement: style, roles, interruptions, learning, limits, sharing, explanations, challenge, override | Partial | Core | Settings are scattered (calm replies, coach, focus, goals). Add `me/agreement.md` (English, German, Polish), read by the agent each session; private for employees; plain text the human edits; nothing inferred. |

### 2E. Protected time

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Time saved is not turned into more work | Missing | Core | A section in the agreement (what you protect saved time for) and an AGENTS.md rule: never fill saved time with suggestions for more output, never propose output targets. No measurement. |

### 2F. Skill resilience

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Skill goals, practice, human-first attempts, explainable handbacks, working without AI | Implemented | Keep | Coach mode, `practice`, `handbook`, onboarding, 'skills I want to keep' in goals. The agreement adds a place for skill goals. |
| Spotting over-dependent workflows | Missing | Defer | Needs evidence of real use. Reconsider when run counts and run cards show work that is always automated and never checked by hand. |

### 2G. Observing the experience of work

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Context switches, focus blocks, resume time, overload, control, energy, open loops | Missing | Defer | Automatic observation would be surveillance; manual logging adds the load it measures. A person who wants to watch one of these can make it the measure of a small experiment (H). Reconsider if testers ask for a self-report log. |

### 2H. Small experiments

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Baseline, change, measure, review, keep, revise or revert | Partial | Module | Only inside `work-audit`. Add an optional `small-experiment` module: one card per experiment with a versioned change, separate human and business measures, and wording rules that forbid causal claims the data cannot support. |
| Counterfactual replay, micro-randomisation | Missing | Defer | Needs recorded data and statistics that a small workspace does not have. Reconsider with a team that runs repeated, comparable work. |

### 2I. Decision and attention escrow

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Park thoughts and decisions with context, what to decide, evidence, next step, review date | Partial | Enhancement | Extend `park` with optional 'to decide' and 'look again on' fields; status lists items whose date has come. Nothing is acted on automatically. |

### 2J. Failure-aware automation

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Scheduled, started, completed, created, verified, delivered, reported | Missing | Enhancement | Living System runs no jobs. Add the seven states to careful-run's verify and hand-back stages, so 'done' always says how far it got. |
| Job runner, retries, missed-run recovery | Missing | Reject | Would need a background service, which Living System avoids by design. Reconsider never for the core; an optional module could document patterns if users automate with their own schedulers. |

### 2K. Choosing where work runs

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Local vs remote, cost, privacy, resources, offline | Partial | Keep | Local-first page, run card 'who does what', the decision-model evaluation. No scheduler. |
| Energy or carbon accounting | Missing | Reject | Cannot be measured from inside Living System; estimates would be speculative claims. |

### 2L. Patterns from other frameworks

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Work decomposition and durable state; hooks, skills, tests; design review; staged context | Implemented | Keep | Careful-run, the guard and skills, the test suite, ICM workflows. Nothing copied, so no new licence terms; ICM is credited. |
| Design and accessibility review for users | Missing | Defer | A development tool rather than a user need; the careful-run website profile has the basic checks. Reconsider if users build interfaces with it. |

### 2M. Federated knowledge

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Personal vs shared, explicit sharing and acceptance, role context, provenance | Implemented | Keep | `link`, `share`, `role-review`, `roles/<role>/`, onboarding. |
| Withdrawing a share | Missing | Enhancement | `share --withdraw` removes your shared file while it still waits for review. Once accepted it is company knowledge, removed through the company's own process. |
| Access control between people | Missing | Reject | Not technically possible with shared folders; claiming it would be false. Folder and git permissions remain the real boundary. |

### 2N. Atlas and pattern commons

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Read-only view of how rules, projects, workflows and knowledge connect | Missing | Enhancement | `living.py atlas`: a Markdown page (with a diagram) built from the files; Markdown stays the source; no database. |
| Pattern commons | Partial | Defer | Modules are shareable patterns already, and contributions go through pull requests. Reconsider with a helper that turns a user's workflow into a module skeleton once people ask to contribute one. |

### 2O. Several perspectives on a decision

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| Structured review from different viewpoints, evidence vs interpretation, bounded, one human decision | Missing | Enhancement | A `perspectives` skill run in one session, using roles (never real people's names or invented quotes), at most two rounds, ending with the human's choice. |

### 2P. Ethics and evidence of value

| Capability | Coverage | Decision | Why |
| --- | --- | --- | --- |
| No dark patterns, surveillance, quotas, hidden profiling, misleading claims | Partial | Core | Practised throughout but not written in one place. Add `docs/ethics.md`: each guardrail and how it is upheld, marking what is enforced and what is a rule. |
| Four separate dimensions: business, human, resources, reliability | Missing | Enhancement | The evidence summary and the experiment card report the four separately and say plainly what was not measured. |

## Not now, and not at all

Every **Defer** and **Reject** above, in one list.

- **Reject** (A) Staging for tasks: Living System is not a task manager; people already have one. Reconsider if several users ask for task hand-offs inside the workspace.
- **Defer** (B) Feedback on routes that worked or failed: Needs real runs first. Reconsider after ten or more recorded runs; then a short 'what worked' line per run card is enough.
- **Defer** (C) Human-readable operational log: The review record, runs, handover and git history already cover what matters. A separate action log grows fast and repeats git. Reconsider if a team needs an audit trail beyond git.
- **Defer** (D) Typed, probability-based decisions for classification and routing: Benchmarked 2026-10-24 (docs/evaluations/laya): Laya's English model picked the right module 72% of the time against 50% for keyword signals, but missed 'approve my pending proposal' and 'change the rule' on risk. Agents already make suggestions in context. Not adopted.
- **Defer** (D) Local vs hosted inference; CPU suitability: Measured on CPU: about 2 s and 2.8 GB of memory per request with three questions, 2.4 GB to download and install. Jev not tested: hosted and proprietary, requests would leave the computer.
- **Defer** (D) Replaceable decision-model adapter with confidence thresholds and fallback: Reconsider only if suggestions are needed without an agent, a few hundred real labelled requests exist for fine-tuning, and the adapter can stay outside the standard-library core. It would only ever suggest, never decide risk or approve.
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
- **Reject** (2B) Technically enforced autonomy limits: Delegations are instructions; the guard's blocks stay as they are and no delegation lifts them. Claiming enforcement would be false. Reconsider only with a mechanism the tools can actually check.
- **Defer** (2F) Spotting over-dependent workflows: Needs evidence of real use. Reconsider when run counts and run cards show work that is always automated and never checked by hand.
- **Defer** (2G) Context switches, focus blocks, resume time, overload, control, energy, open loops: Automatic observation would be surveillance; manual logging adds the load it measures. A person who wants to watch one of these can make it the measure of a small experiment (H). Reconsider if testers ask for a self-report log.
- **Defer** (2H) Counterfactual replay, micro-randomisation: Needs recorded data and statistics that a small workspace does not have. Reconsider with a team that runs repeated, comparable work.
- **Reject** (2J) Job runner, retries, missed-run recovery: Would need a background service, which Living System avoids by design. Reconsider never for the core; an optional module could document patterns if users automate with their own schedulers.
- **Reject** (2K) Energy or carbon accounting: Cannot be measured from inside Living System; estimates would be speculative claims.
- **Defer** (2L) Design and accessibility review for users: A development tool rather than a user need; the careful-run website profile has the basic checks. Reconsider if users build interfaces with it.
- **Reject** (2M) Access control between people: Not technically possible with shared folders; claiming it would be false. Folder and git permissions remain the real boundary.
- **Defer** (2N) Pattern commons: Modules are shareable patterns already, and contributions go through pull requests. Reconsider with a helper that turns a user's workflow into a module skeleton once people ask to contribute one.

## Risks to watch

- Sunday's test now covers more: every increment adds checklist steps, and agent behaviour (skills, coach, focus) is only verified live.
- Instruction growth: each rule makes AGENTS.md longer. Keep each rule to a few lines and prefer skills for procedures.
- Content modules can look like promises. Each says what it does not do.
- Decision models (D) stay out of the core unless a benchmark you approve shows a clear gain.

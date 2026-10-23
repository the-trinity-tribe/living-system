# Living System

**Experimental · local-first Human–AI work environment**

Living System is a way to give your AI agent a **written memory you control**.

What it is designed to give you:

- **Your rules, written down.** Your agent reads them at the start of each session instead of guessing.
- **You stay the decision-maker.** The agent can *propose* a change. Only you approve it.
- **A trail you can read.** Every rule is a plain file that says where it came from and what it replaced.
- **Less lost context.** A handover note lets the next session continue where the last one stopped.
- **Yours, on your computer.** Plain Markdown files and one small Python tool (standard library only). No server, no account, no tie to one AI vendor.

Whether it helps *you* is something you can test: the workspace includes a small [value check](core/template/value-check/README.md) you run yourself.

Created and architected by **Adrianna Mamczarz**, through **The Trinity Tribe**. AI assisted with implementation; design decisions, review, and acceptance remained human-led.

> **Status:** An experimental, educational reference implementation. Not a security boundary, identity-verification system, or production-ready access-control product. Moss & Circuit, Riverside Community Garden and every person named in the example (including Maya Chen, Leo and Sam) are fictional, and all project details in the example are invented.

**New here?** Read [docs/ai-tools.md](docs/ai-tools.md) to see which AI tool you need, then follow the quick start below. Every feature has a plain-language page in [docs/](docs/README.md).

## Three things to keep apart

| | What it is | Where |
| --- | --- | --- |
| **The product** (this repository) | The template, the tools and the docs. Public. | You are here. |
| **Your workspace** | Your own private folder, made by `init`. | A separate folder you choose, **outside** this repository. |
| **The demo** | A fictional sandbox to explore. Not your workspace. | [demo/moss-and-circuit/](demo/moss-and-circuit/) |

Your workspace is created in its own folder on purpose: personal data should never sit inside a clone of a public repository.

## Quick start

**Requirements:** Git (to clone) and Python 3.10 or newer. No third-party packages or accounts. The tests run automatically on Linux, Windows and macOS (`.github/workflows/tests.yml`).

```sh
git clone https://github.com/the-trinity-tribe/living-system.git
cd living-system
```

**On Windows:** type `py` where this page says `python3` (for example `py tools/living.py doctor %USERPROFILE%\my-workspace`). If `py` is not found, install Python from python.org and tick "Add python.exe to PATH". In PowerShell, `~\my-workspace` also works for a folder in your home directory. Use the same `/` or `\` style throughout one command.

### Make your own workspace

The easiest way is to open this repository in Claude Code or Codex and say *"Read INSTALL.md and set up my workspace."* The agent asks you up to five short questions (plus whether to keep replies short), shows you what it will create, and waits for your yes. See [INSTALL.md](INSTALL.md).

Or do it yourself. Profiles: `student`, `professional`, `employee`, `manager`.

```sh
python3 tools/living.py init ~/my-workspace --profile professional --language en --calm-replies
python3 tools/review.py --root ~/my-workspace check
```

`init` refuses a folder that already has files in it, and leaves nothing behind if it fails. To undo: delete the folder.

Your starter `SYSTEM.md` and `PRINCIPLES.md` are **drafts** until you change them to `status: approved` yourself.

### Add only what you need

Optional modules add a ready-made workflow or knowledge area. Nothing is installed unless you ask, and every command only shows a plan until you add `--apply`.

| Module | What it gives you |
| --- | --- |
| `weekly-update` | A three-step weekly update: gather facts, draft, check who approves. You send it. |
| `meeting-notes` | Meeting notes become clean notes, actions, and proposals for anything that would change a rule. |
| `staged-learning` | Your agent suggests lessons from its mistakes; only lessons you approve are used next time. |
| `knowledge-inbox` | Your agent suggests knowledge worth keeping, with its source; only what you approve is kept, and old facts are flagged for a re-check. |

```sh
python3 tools/living.py modules --workspace ~/my-workspace        # what is available
python3 tools/living.py add ~/my-workspace weekly-update          # see the plan
python3 tools/living.py add ~/my-workspace weekly-update --apply  # install it
python3 tools/living.py remove ~/my-workspace weekly-update       # see what removal would do
```

`add` never overwrites a file. `remove` deletes only files you have not edited, and never touches your decisions, proposals or projects. Each module's `README.md` in [modules/](modules/) answers the same ten questions (template: [docs/features/_template.md](docs/features/_template.md)).

**Your own workflow:** ask your agent, for example, *"Create a workflow for planning a launch post."* It proposes the stages, shows the plan, and after your yes creates the folders with `new-workflow` (staged in the style of ICM, see [CREDITS.md](CREDITS.md)):

```sh
python3 tools/living.py new-workflow ~/my-workspace launch-post --stages research,draft,review --goal "A launch post ready for my review"
```

**Your first rule in two minutes:** after setup, tell your agent *"Help me make my first decision from my setup answers."* It drafts the rule, asks you about the wording, and you approve it yourself. (`python3 tools/living.py propose` writes any proposal in the right format without you typing it.)

**Automate only what really repeats:** your agent counts repeated work (`python3 tools/living.py runs ~/my-workspace` shows the count) and asks you at the third time whether to automate it, keep it manual or decide later.

**Your rules stay yours:** a small guard stops the agent from editing your decisions or approving your drafts directly ([write guard](docs/features/write-guard.md)).

**What needs my attention?** `python3 tools/living.py status ~/my-workspace` lists the proposals waiting for your review, lesson suggestions, drafts you have not approved, and where the last session stopped. It changes nothing.

**Health check:** `python3 tools/living.py doctor ~/my-workspace` reads your workspace and lists problems in plain words (for example a draft you have not approved yet, a workflow step left unfinished, or demo material that slipped in). It changes nothing.

**Backup or move:** `python3 tools/living.py export ~/my-workspace ~/backup.zip --apply` packs everything into one zip file ([export](docs/features/export.md)).

**Getting a newer version:** after you update this folder (for example with `git pull`), run `python3 tools/living.py upgrade ~/my-workspace` to see what would change, then add `--apply`. Files you never changed are updated; files you edited are kept, with the new version saved in `.living/upgrade/` to compare; your decisions, proposals, projects and personal goals are never touched.

### Explore the demo

```sh
python3 -B tools/review.py --root demo/moss-and-circuit current
python3 -B tools/review.py --root demo/moss-and-circuit check
python3 -B -m unittest discover tests
```

These commands **read and check** the fictional example. `current` lists active approved decisions; `check` reports certain structural problems; the unit tests exercise the governance rules and workspace creation. Passing them does **not** verify the identity of a reviewer, or guarantee security or agent correctness.

For a scripted 10-minute live demo on temporary copies, see [demo/WALKTHROUGH.md](demo/WALKTHROUGH.md).

## Explore the worked example

The demo contains one small fictional organisation, **Moss & Circuit**, and its **Riverside Community Garden** project.

1. Read [demo/moss-and-circuit/AGENTS.md](demo/moss-and-circuit/AGENTS.md) for agent instructions, authority boundaries and human-review rules.
2. Follow [CONTEXT-ROUTING.md](demo/moss-and-circuit/CONTEXT-ROUTING.md) to read only the context relevant to a task.
3. Open the [project file](demo/moss-and-circuit/projects/riverside-community-garden.md), then the **current** approved decision it points to.
4. Inspect [proposals/](demo/moss-and-circuit/proposals/) and [decisions/](demo/moss-and-circuit/decisions/) to see the evidence, a human-attributed review, the superseded decision and the resulting current decision.
5. Open the hand-written [client-update workflow](demo/moss-and-circuit/workflows/client-update/CONTEXT.md), a labelled example of working in stages with a human checkpoint after each one.

The example demonstrates this lifecycle:

```text
routed context → contradictory evidence → staged proposal
    → explicit human review → new approved decision
    → old decision retained as history → fresh-agent reuse
```

**Authority is not a role label.** Project notes and proposals cannot override current approved decisions. A `promoted` proposal records provenance; it is not current operating authority. See [AGENTS.md §2–7](core/template/AGENTS.md).

## Working with an agent

Use a **fresh session** with the workspace (or the demo folder) as its working directory. Ask the agent to start at `AGENTS.md` and route through `CONTEXT-ROUTING.md`. For a cold-open exercise, do not supply private conversations, external development handoffs or an expected-answer sheet. Observe which files were actually consulted and whether the agent separates approved facts from proposals and uncertainty.

The example's expected test answers are intentionally **not** stored in the demo, to avoid supplying an answer key to a new agent.

## Review operations and safety

`tools/review.py` also supports `hash` and `review`. Unlike `current` and `check`, the `review` operation **modifies shared files** and must be run only after a human explicitly decides the outcome of a **named, currently reviewable proposal**:

```text
python3 tools/review.py --root <workspace> hash decisions/path-to-current-decision.md
python3 tools/review.py --root <workspace> review proposals/path-to-pending-proposal.md --outcome approve|reject|defer --by "Reviewer Name"
```

The second line illustrates the CLI syntax (`approve|reject|defer` means choose exactly one). **Do not run it against the shipped demo.** An approval creates a new decision and marks the proposal as promoted; rejection or deferral leaves canonical decisions unchanged. A proposal can add a first rule (`kind: new`), add an exception (the default), replace a rule completely (`kind: replace`) or retire one so no rule applies (`kind: retire`). In every case the old decision file stays unchanged as history. The recorded reviewer name is an **attribution field, not authenticated identity**. For exact safeguards and refusal rules, see [AGENTS.md §7](core/template/AGENTS.md) and the [review tool](tools/review.py).

## Credits

See [CREDITS.md](CREDITS.md).

## Current scope and limitations

- The review mechanism demonstrates context routing, canonical decisions, evidence-bounded proposals, explicit review and deterministic promotion.
- Living System is designed to support fresh-session reuse through explicit, human-readable context and governance rules.
- There is **no authentication or identity attestation**: `--by`, `approved_by` and similar labels are unverified declarations.
- There is no automatic approval, secret store, multi-user authorization, hosted product, automatic private-data extraction, or guarantee that an agent will comply with instructions. The write guard (`docs/features/write-guard.md`) blocks agent edits to decisions in Claude Code, and in Codex after you trust its hooks; it is a guard rail, not a security boundary.
- Starter files come in English, German and Polish. The agent's rule files stay English in every language, and the tools print English messages. The German and Polish texts would benefit from review by native speakers.
- The profile files (`student`, `professional`, `employee`, `manager`) are small starting points, not tested against real use.
- Modules, `new-workflow` and `doctor` are new and experimental. Module suggestions and counting repeated work are instructions to the agent: nothing watches your work in the background, and the count holds only short names and dates.
- The fictional organisation is a demonstration, not a recommended deployment with real client or personal data. Review any material before putting it in an AI agent's context or publishing a repository.

## Licensing, community and credit

Living System's repository files are distributed under the **[Mozilla Public License 2.0](LICENSE)** (`MPL-2.0`). Covered modifications distributed to others are subject to the licence's obligations. Independently created files or organisational data are **not automatically MPL-covered merely because someone uses Living System**, though copying covered template material into them may affect the analysis. Read the licence for exact terms.

Copyright © 2026 Adrianna Mamczarz, for copyrightable original material to which she holds rights. The Trinity Tribe is the project home. Contributions are welcome under the repository licence; see [CONTRIBUTING.md](CONTRIBUTING.md). Please credit the creator and other contributors when discussing or building upon this work.

Forks and independent implementations are welcome, but should not imply official approval or affiliation with The Trinity Tribe. For vulnerability reporting, see [SECURITY.md](SECURITY.md).

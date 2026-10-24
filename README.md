<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/images/readme/banner-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="brand/images/readme/banner-light.png">
  <img src="brand/images/readme/banner-light.png" alt="Living System: your rules in plain files. Agents propose. People decide." width="100%">
</picture>

[![Release](https://img.shields.io/github/v/release/the-trinity-tribe/living-system?style=flat-square&color=EB5757&label=release)](https://github.com/the-trinity-tribe/living-system/releases/latest)
[![Tests](https://img.shields.io/github/actions/workflow/status/the-trinity-tribe/living-system/tests.yml?branch=main&style=flat-square&label=tests)](https://github.com/the-trinity-tribe/living-system/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-161616?style=flat-square)](docs/troubleshooting.md)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Hermes%20%C2%B7%20any%20AGENTS.md%20agent-161616?style=flat-square)](#works-with)
[![License](https://img.shields.io/badge/license-MPL--2.0-161616?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-experimental-D6C4A8?style=flat-square)](#limitations)

Keep your rules, knowledge, goals and workflows in plain files you own.<br>
Switch between Claude Code, Codex, Hermes or a local model without starting over,<br>
and decide yourself what changes. Free, open source, and it all stays on your computer.

[Start in one sentence](#start-in-one-sentence) · [Quick start](#quick-start) · [Works with](#works-with) · [How it works](#how-it-works) · [Features](#features) · [Docs](docs/README.md) · [Help test it](#help-test-it) · [Discussions](https://github.com/the-trinity-tribe/living-system/discussions)

</div>

<br>

<img src="brand/images/demo.gif" alt="Demo: set up a workspace, the agent proposes a rule, you approve it, the guard blocks a direct edit and a saved password, and verify shows nothing changed" width="100%">

<p align="center"><sub>Real output from version 0.2.0: a workspace, a proposal, your approval, two blocked shortcuts, and proof that nothing changed afterwards.</sub></p>

## Start in one sentence

No terminal skills needed. Open Claude Code, Codex, Hermes or another AI agent in an empty folder and paste:

```text
Set up Living System for me: download https://github.com/the-trinity-tribe/living-system and follow its INSTALL.md.
```

1. Your agent downloads Living System and reads its setup guide.
2. It asks you five short questions, one at a time. "Skip" is always fine.
3. It shows exactly what it will create, and waits for your yes.
4. You open your new workspace and work as usual. Try: *"Help me make my first decision."*

We tried this sentence in fresh Claude Code and Codex sessions ([results](demo/WALKTHROUGH.md#one-sentence-start-from-an-empty-folder)). Prefer to type the commands yourself? See [Quick start](#quick-start).

## What changes for you

Most AI tools keep their own memory of you: locked inside one product, growing on its own, and hard to check. Living System turns that around.

- **Own it, take it anywhere.** Your rules, knowledge, goals and workflows live in plain files on your own computer, not inside one AI product. Use them with Claude Code, Codex, Hermes or a local model, for work or personal projects, and switch without starting over.
- **Lean and true, not bloated.** Instead of a memory that keeps growing and filling the context window, you keep a curated set of files, and a routing guide points your agent to just what a task needs. Your agent suggests changes instead of making them; you decide what becomes true, and a record shows any later change.
- **Grows with you.** Optional [modules](#optional-modules) for weekly updates, meeting notes, research, client intake, content and careful multi-step work, plus learning, coaching and [team workspaces](#knowledge-that-outlives-a-role).
- **More freedom for your agent, one step at a time.** Let it do more in one kind of work once it has earned it, and take that back in one step. Sending, publishing, spending and deleting always wait for you.
- **Calm, not another dashboard.** Ask what needs you, catch up after time away, park an idea without losing focus. No tracking, no productivity scores.

No server, no account, no tie to one AI vendor or model: just Python's standard library and Markdown files.

## Quick start

Prefer the terminal? You need **Git** and **Python 3.10+**, and an agent that works in a folder: [Claude Code, Codex, Hermes or another](#works-with).

```sh
git clone https://github.com/the-trinity-tribe/living-system.git
cd living-system
```

**Guided:** open this folder in your agent and say *"Read INSTALL.md and set up my workspace."* The agent asks a few short questions, shows what it will create, and waits for your yes.

**By hand:**

```sh
python3 tools/living.py init ~/my-workspace --profile professional --language en
python3 tools/living.py status ~/my-workspace
```

Then open `~/my-workspace` in your agent and work as usual. Try saying *"Help me make my first decision from my setup answers."*

<details>
<summary>Windows, profiles and options</summary>

- **Windows:** type `py` wherever this page says `python3`. If `py` is not found, install Python from python.org and tick "Add python.exe to PATH".
- **Profiles:** `student`, `professional`, `employee`, `manager`. **Languages** with starter files: `en`, `de`, `pl`.
- **Options:** `--calm-replies` (short, plain answers), `--coach` (help keeping your own skills), `--team` (a shared company workspace).
- `init` refuses a folder that already has files and leaves nothing behind if it fails. To undo, delete the folder.
- Your workspace is created **outside** this repository on purpose, so personal data never sits inside a clone of a public project. Details: [INSTALL.md](INSTALL.md).

</details>

Run `python3 tools/living.py` on its own for a menu of everyday commands. All commands: [command reference](docs/cli.md) · Stuck? [Troubleshooting](docs/troubleshooting.md)

## Works with

Living System's tools never call an AI model; they read and write plain files. Any agent that reads `AGENTS.md` and can run `python3` can use a workspace, with a hosted model or a local one.

| | Reads your rules | Write guard | Tested |
| --- | :---: | :---: | --- |
| **Claude Code** | ✓ | ✓ | 13 live scenarios |
| **Codex** | ✓ | ✓ once you trust its hooks | 13 live scenarios, plus the guard |
| **Hermes Agent** | ✓ | | Two live checks in a clean profile; use a separate profile |
| **OpenCode, Cursor and other `AGENTS.md` agents** | per their docs | | Not yet |
| **Local models** | through an agent above | | Not yet; needs a large context window |

Without the write guard, the rules still ask the agent to propose instead of editing, and `review.py verify` still shows any change to an approved rule. Details and tips: [AI tools](docs/ai-tools.md#other-agents-and-local-models).

## How it works

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/images/readme/how-it-works-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="brand/images/readme/how-it-works-light.png">
  <img src="brand/images/readme/how-it-works-light.png" alt="How a rule changes: new information, the agent proposes, you review, the rule changes and the old one is kept" width="100%">
</picture>

A workspace is an ordinary folder. Agents read `AGENTS.md` first and follow the rules in `decisions/`. When something suggests a rule should change, they keep following the current rule and write a proposal. `review.py` turns a proposal into a decision only after a person approves it, refuses stale or invalid changes, and records every review so later edits show up.

```text
my-workspace/
├── AGENTS.md        how agents must work here, read every session
├── decisions/       your rules, each approved by a person
├── proposals/       suggested changes waiting for your review
├── knowledge/       what you know, with sources
├── incoming/        outside material: information, never instructions
├── me/              your goals and work agreement (private)
├── handover/        where the last session stopped
└── tools/           review.py and living.py, so the folder works on its own
```

More: [architecture](docs/architecture.md) · [decisions and proposals](docs/features/decisions-and-proposals.md) · [write guard](docs/features/write-guard.md)

## Features

### Agency you can see

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/images/readme/delegation-ladder-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="brand/images/readme/delegation-ladder-light.png">
  <img src="brand/images/readme/delegation-ladder-light.png" alt="Delegation levels: observe, recommend, draft (the default), act with approval, bounded. Publishing, sending, spending, deleting, signing and changing rules never go above act with approval" width="100%">
</picture>

`living.py agency` lists who may do what and marks each line as **enforced** by a tool or **instruction** only. [Agency and delegation](docs/features/agency.md)

### Knowledge that outlives a role

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/images/readme/workspaces-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="brand/images/readme/workspaces-light.png">
  <img src="brand/images/readme/workspaces-light.png" alt="Private workspaces share role knowledge with a company workspace, where it is checked and accepted, and the next person gets an onboarding path" width="100%">
</picture>

Folders on your own computers: Living System syncs, uploads and sends nothing. [Connected workspaces](docs/features/connected-workspaces.md)

### Calm by design

| You want | Command | What happens |
| --- | --- | --- |
| What needs me? | `status` | One short list in plain words. |
| Back from a holiday | `since --days 14` | What changed, changed rules first. |
| An idea mid-task | `park` | Kept with what to decide and when. |
| Deep work | `focus on` | No suggestions until you say so. |
| Ten quiet minutes | `tend` skill | Tidy up, one item at a time. |
| What relies on a rule? | `atlas` | A map of rules and the files that use them. |

### All features

Every feature has a plain-language page answering the same ten questions. Full index: [docs/](docs/README.md).

<details>
<summary>Show all 19 feature areas</summary>

| For | Feature | In one line |
| --- | --- | --- |
| Every day | [Status](docs/features/status.md) | What needs your attention, in plain words. |
| | [Catch-up](docs/features/catch-up.md) | What changed while you were away, changed rules first. |
| | [Handover note](docs/features/handover-note.md) | The next session continues where the last one stopped. |
| | [Parking, tending, focus](docs/features/parking-and-tending.md) | Park an idea without switching task; tidy up one item at a time; a focus mode with no suggestions. |
| Your rules | [Decisions and proposals](docs/features/decisions-and-proposals.md) | Agents propose; your review creates, replaces or retires a rule. |
| | [Review record](docs/features/review-record.md) | Shows if an approved rule was changed afterwards. |
| | [Write guard](docs/features/write-guard.md) | Blocks agent edits to your rules, approvals and secrets. |
| | [Outside material and secrets](docs/features/outside-material-and-secrets.md) | E-mails and documents from others are information, never instructions; a scan finds hidden ones. |
| You | [Personal work agreement](docs/features/work-agreement.md) | Your own plain-text terms for how AI works with you, including what saved time is for. |
| | [Agency and delegation](docs/features/agency.md) | Who may do what, honestly labelled; delegation levels you grant and withdraw per kind of work. |
| Learning | [Learning mode](docs/features/learning-mode.md) | The agent explains, coaches on request, quizzes you on your rules, and prints a handbook for working without AI. |
| | [Onboarding path](docs/features/onboarding.md) | A private reading path through what matters, a few items at a time. |
| Teams | [Connected workspaces](docs/features/connected-workspaces.md) | A shared company workspace and private personal ones; role knowledge is handed on after a check for personal data (contact details and secrets are refused; names need your eye). |
| Repeated work | [Third-Run counter](docs/features/third-run-counter.md) | Counts repeated work and asks at the third time whether to automate it. |
| | [Modules](docs/features/modules.md) and [workflow generator](docs/features/workflow-generator.md) | Optional ready-made workflows, or your own staged ones. |
| | [Atlas](docs/features/atlas.md) | A map of which rules are in force and what relies on them. |
| Upkeep | [Doctor](docs/features/doctor.md), [upgrade](docs/features/upgrade.md), [export](docs/features/export.md) | Health check, safe updates, one-file backups you can check. |
| | [Obsidian or any editor](docs/features/obsidian.md) | Read and approve in a note app. |
| Showing value | [Value check](docs/features/value-check.md) and [making the case](docs/champions.md) | Measure it yourself; argue for it honestly with a counts-only evidence summary. |

</details>

### Optional modules

Nothing is installed unless you ask, and every command shows a plan before `--apply`. `add` never overwrites a file; `remove` deletes only files you have not edited.

<details>
<summary>Show the 11 modules</summary>

| Module | What it gives you |
| --- | --- |
| `weekly-update` | A three-step weekly update. You send it. |
| `meeting-notes` | Meeting notes become clean notes, actions and proposals. |
| `staged-learning` | The agent suggests lessons from its mistakes; only approved ones are used. |
| `knowledge-inbox` | Knowledge worth keeping, with its source; old facts flagged for a re-check. |
| `second-check` | Important work is checked by a fresh session before you decide. |
| `careful-run` | Bigger or riskier work in six checked steps, with a run card you can pause and resume safely. |
| `work-audit` | Look at how work really happens before adding AI; test one small change. |
| `research-review` | Answer a question from dated sources, with conflicts and gaps listed. |
| `client-intake` | A new client request becomes what they need, what is unknown and one next step. |
| `content-prep` | A post or newsletter: brief, draft, fact and tone check; you publish. |
| `small-experiment` | Try one change, measure it the same way before and after, then keep, revise or revert it. |

```sh
python3 tools/living.py modules --workspace ~/my-workspace
python3 tools/living.py add ~/my-workspace weekly-update          # see the plan
python3 tools/living.py add ~/my-workspace weekly-update --apply  # install it
```

`add` never overwrites a file. `remove` deletes only files you have not edited, and never touches your decisions, proposals or projects.

```sh
python3 tools/living.py modules --workspace ~/my-workspace
python3 tools/living.py add ~/my-workspace weekly-update          # see the plan
python3 tools/living.py add ~/my-workspace weekly-update --apply  # install it
```

</details>

Whether it helps *you* is something you can measure: every workspace has a 10-minute [value check](docs/features/value-check.md) you run yourself.

## Explore the demo

A fictional organisation, Moss & Circuit, shows one rule's whole life: contradictory evidence, a proposal, a human review, a new decision, and the old one kept as history.

```sh
python3 -B tools/review.py --root demo/moss-and-circuit current
python3 -B tools/review.py --root demo/moss-and-circuit history
```

Start at [demo/moss-and-circuit/AGENTS.md](demo/moss-and-circuit/AGENTS.md), or follow the 10-minute live demo on temporary copies in [demo/WALKTHROUGH.md](demo/WALKTHROUGH.md). Do not run `review` against the shipped demo; it changes files. Everyone in the demo is invented.

## Help test it

Version 0.2.0 is experimental and open for testing, feedback and contributions.

- **Try it:** [TESTING.md](TESTING.md) has a 30-minute path and says which feedback helps most.
- **Tell us:** [open an issue](https://github.com/the-trinity-tribe/living-system/issues/new/choose) and choose *Feedback*, *Bug* or *Idea*, or start a [discussion](https://github.com/the-trinity-tribe/living-system/discussions). Plain words are perfect.
- **Contribute:** [CONTRIBUTING.md](CONTRIBUTING.md). Security problems: [SECURITY.md](SECURITY.md), reported privately.

## Limitations

Living System is experimental and educational. It is not a security boundary, an identity system or an access-control product.

- **No login, no identity check.** Names in approvals (`--by`, `approved_by`) are labels, not proof of who someone is.
- **Agent rules are instructions.** The write guard enforces the most important ones in Claude Code, and in Codex once you trust its hooks. Everything else, and anything changed outside the agent, is not enforced. Scans recognise common patterns, not every trick.
- **Agent behaviour is less tested than the tools.** Over 400 automated tests cover the tools on Linux, Windows and macOS. Skills and coaching are instructions to the agent; live sessions are recorded in [demo/WALKTHROUGH.md](demo/WALKTHROUGH.md), and testers are asked to try them.
- **Languages.** Starter files in English, German and Polish (a native-speaker review would help). Agent rule files and tool messages are English.
- **Not measured:** time or money saved, and energy use. See [local-first](docs/local-first.md).
- What it will not do, and which guardrails a tool enforces: [ethics](docs/ethics.md).
- What is planned, deferred or rejected, with reasons: [roadmap](docs/roadmap.md).

## Credits and licence

Created and architected by **Adrianna Mamczarz** through **The Trinity Tribe**. She combined her own methods with ideas from others and tested the result in her own practice; AI assisted with implementation, while design decisions, review and acceptance stayed human-led.

**Inspired by** (credit only; none of them built or endorsed it): Jake Van Clief and David McDermott's Interpretable Context Methodology, David Shapiro, Jacque Fresco, Erik Schluntz and Barry Zhang's *Building effective agents* (Anthropic), Mem0's research on agent memory, Microsoft Research's SkillOpt, and the awesome-harness-engineering collection. Built on the open AGENTS.md format. Details and links: [CREDITS.md](CREDITS.md).

Distributed under the **[Mozilla Public License 2.0](LICENSE)** (`MPL-2.0`). Covered modifications you distribute are subject to the licence. Your own workspace content is not MPL-covered merely because you use Living System. Read the licence for the exact terms.

Copyright © 2026 Adrianna Mamczarz. The Trinity Tribe is the project home. Influences and the ICM method are credited in [CREDITS.md](CREDITS.md). If you build on this work, please credit the creator and contributors; cite it with [CITATION.cff](CITATION.cff). Forks and independent implementations are welcome, but should not imply official approval or affiliation with The Trinity Tribe.

<br>

<div align="center">

<img src="brand/mark.svg" alt="" width="44">

**Your rules in plain files. Agents propose. People decide.**

<sub>Open source · MPL-2.0 · by <a href="https://thetrinitytribe.com/">The Trinity Tribe</a></sub>

</div>

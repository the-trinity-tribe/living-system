# How Living System is built

Status: EXPERIMENTAL. Version: 0.3.0.

A short overview for anyone who wants to understand or contribute. No code knowledge needed for the first two sections.

## The idea in one picture

```text
   you (decide)                         your AI agent (Claude Code or Codex)
        │                                        │ reads at the start of every session
        ▼                                        ▼
   ┌──────────────────────────── your workspace (plain files) ────────────────────────────┐
   │ AGENTS.md          the rules for the agent: authority order, what it may and may not do │
   │ CONTEXT-ROUTING.md which file to read for which question (small context, not everything)│
   │ SYSTEM.md, PRINCIPLES.md, decisions/   your rules: canonical once you approve them      │
   │ proposals/         suggested changes: never truth until you review them                 │
   │ projects/, knowledge/, workflows/, lessons/, incoming/   working and background context │
   │ me/                your goals, work agreement, parked ideas, onboarding (private)       │
   │ handover/          where the last session stopped                                       │
   │ .living/           settings, the list of installed files, counts                        │
   │ tools/review.py, tools/guard.py   the review tool and the write guard                   │
   └─────────────────────────────────────────────────────────────────────────────────────────┘
        ▲
        │ creates, checks, upgrades (never decides for you)
   the Living System folder: tools/living.py, templates, modules, docs
```

## Who decides what

1. **Your current instruction** to the agent, for the task at hand.
2. **Canonical files:** `SYSTEM.md` and `PRINCIPLES.md` once approved, and decisions in force.
3. **Project context**, then **background knowledge**.
4. **The agent's own inference**, last.

Proposals are on no level: they are suggestions. Only `review.py review`, run after a human decides, turns one into a decision, and the old decision is kept as history. Full rules: `core/template/AGENTS.md`. What a tool enforces and what is an instruction: `living.py agency`.

## The tools

| Tool | Role | Runs where |
| --- | --- | --- |
| `tools/living.py` | Creates and upgrades workspaces; modules; status, catch-up, doctor, scans, atlas, evidence; parking, focus, onboarding; delegation proposals; connected workspaces. Never approves anything. | The Living System folder |
| `tools/review.py` | Reviews proposals, keeps decision history and the chained review record, checks structure. Copied into each workspace, so a workspace works on its own. | Each workspace |
| `tools/guard.py` | The write guard: Claude Code and Codex run it before an agent changes a file, and it exits with a block for protected changes. | Each workspace |
| `tools/release_check.py` | Keeps private names, personal paths, e-mail addresses and secrets out of this public repository. | The repository |

All four use only the Python standard library, write UTF-8 with LF line endings, refuse to write through links, and change nothing when they refuse.

## Building blocks

- **Templates** (`core/template/`), **profile overlays** (`core/profiles/`) and **translations** (`core/i18n/`) make up a new workspace. The agent rule files stay English.
- **Skills** (`core/skills/`) are short procedures copied to `.claude/skills/` and `.agents/skills/`, so both agents get the same ones.
- **Modules** (`modules/<id>/`) are optional: a `module.json` (what it installs, its routing row, what needs approval, signal phrases), a `README.md` and the files. Most are staged workflows in the style of ICM (see `CREDITS.md`): numbered stage folders, each with a `CONTEXT.md` (inputs, process, outputs, checkpoint) and an `output/` folder.
- **The manifest** (`.living/manifest.json`) records the fingerprint of every installed file, so `upgrade` and `remove` only touch files you never changed.

## What is not here, on purpose

No server, database, background process, network access, account or login. Agents run under your own account with their providers. Decisions about when to add something are recorded in the [roadmap](roadmap.md); guardrails in [ethics](ethics.md).

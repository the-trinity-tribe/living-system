# Feature: careful run

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `careful-run`.

## What does this feature do?

It gives bigger or riskier work six steps, each with a stop: **frame** (what is wanted, in one card), **plan** (steps, scope, how to undo), **make**, **check** (a fresh session that did not make it), **verify** (tools and tests, not opinions) and **hand back** (what was done, what is open). Everything about the run lives in one **run card**, so you can pause today and resume tomorrow, with any agent.

## Why would someone need it?

Big tasks go wrong in familiar ways: the goal drifts, the scope quietly grows, the maker checks their own work, and after a break nobody knows which files changed. The run card and the checkpoint make those visible.

## What problem does it solve?

- Scope is written down; anything beyond it needs your yes.
- High-risk runs (publishing, sending, spending, deleting, changing rules, touching the company workspace) need your yes on the plan.
- The checker is never the maker.
- Before resuming, `living.py checkpoint` says which files changed since the last stop.

## What does it require?

A Living System workspace, Python 3.10 or newer, and Claude Code or Codex. Works alongside `second-check`; it does not need it.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace careful-run
python3 tools/living.py add ~/my-workspace careful-run --apply
```

## How do you use it?

Say "let's do this as a careful run". The agent copies `references/run-card.md` to `runs/<date>-<name>.md` and fills it in with you. At each stop it updates the card. To pause, it records a checkpoint:

```sh
python3 tools/living.py checkpoint ~/my-workspace workflows/careful-run/runs/2026-10-24-website.md --record
```

To resume, it runs the same command without `--record` and tells you what changed.

## Example scenarios

- Moving a website to a new host: frame and plan list every file and how to roll back; the check runs in Codex; verify runs the site's own tests; hand back lists what is left.
- A two-day research report: pause on day one with a checkpoint; on day two the agent sees two source notes changed and re-reads them before continuing.

## What changes inside the system when it runs?

Files are written only inside `workflows/careful-run/`: the run card and stage outputs. `checkpoint --record` rewrites the card's Checkpoint section. Nothing else changes.

## Where does the human keep control?

You approve the plan of every high-risk run and anything beyond scope, and you decide in hand back. The checker reports; it never edits.

## What can go wrong, and how do you undo it?

- **The card gets out of date.** The agent updates it at each stop; if it did not, say so and it reconstructs it from the files.
- **A checkpoint misses a file.** Only files listed under "Files in scope" are fingerprinted. Add the file and record again.
- Remove the module with `living.py remove`; your run cards are kept if you edited them.

# Feature: doctor

Status: EXPERIMENTAL. Version: 0.3.0.

## What does this feature do?

`doctor` is a health check for your workspace. It reads your files and lists problems in plain words. It changes nothing in your workspace.

## Why would someone need it?

A workspace is plain files, so it is easy to break by accident: a draft you forgot to approve, a half-finished workflow, a module with a missing file, or demo material copied in. `doctor` finds these. It also points out workflows and knowledge that refer to a replaced, retired or missing decision; knowledge files that look like duplicates; knowledge marked `confidence: low`; a `knowledge/` folder that has grown flat (time for topic drawers); and an `AGENTS.md` that has grown much longer than installed. It also reports anything that looks like a password or key, invisible characters, and files with text addressed to an AI (details: `living.py scan`).

## What problem does it solve?

You do not have to know where to look. It also catches things that could make an agent follow the wrong rules, such as a second `AGENTS.md` hidden in a sub-folder.

## What does it require?

Python 3 and the Living System folder (the check lives there, not in your workspace). The workspace needs `.living/manifest.json`, which `init` creates.

## How do you install or enable it?

Nothing to install.

## How do you use it?

To keep or share a copy of the result: `python3 tools/living.py doctor ~/my-workspace --out ~/Documents/health.md` (saved outside the workspace only).


```sh
python3 tools/living.py doctor ~/my-workspace
```

Run it from the Living System folder. It prints one line per finding, most serious first, then a count.

| Level | Meaning |
| --- | --- |
| `ERROR` | Something is broken or unsafe. Fix it. |
| `WARN` | Something is unfinished or may surprise you. |
| `INFO` | A note. Often "a proposal waits for you". |

Exit codes: `0` no errors (warnings and notes still exit 0), `1` at least one `ERROR`, `2` it could not run (`REFUSED`, for example the folder is not a workspace or `.living/manifest.json` is damaged).

A clean workspace prints `All good: no problems found.` A fresh one prints two warnings that `SYSTEM.md` and `PRINCIPLES.md` are not approved yet.

### What it checks

**Errors**

- Everything `python3 tools/review.py check` reports: missing root files (`AGENTS.md`, `CONTEXT-ROUTING.md`, `SYSTEM.md`, `PRINCIPLES.md`, `README.md`), routing rows pointing at missing files, unreadable or unexpected decision files, a `supersedes:` pointing at a missing decision, bad retirement records, proposals with missing keys or mismatched `kind` and `target`, and project files that point at a superseded decision.
- An agent instruction file (`AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `CLAUDE.local.md`, `GEMINI.md`, in any letter case) inside a sub-folder. An agent may load it as a second set of rules. Move its content into a `CONTEXT.md`.
- A `.claude`, `.codex`, `.agents` or `.cursor` folder nested inside another folder.
- Demo content: a file identical to one only the demo ships, or a Markdown file containing the demo banner "DEMO — fictional sandbox".
- `tools/review.py` missing.
- A module installed but with no row in `CONTEXT-ROUTING.md`, a row for a module that is not installed, or a row pointing at a file that does not exist.

**Warnings**

- `AGENTS.override.md` or `CLAUDE.local.md` in the workspace root. Some agents read them instead of, or on top of, `AGENTS.md`.
- `tools/review.py` differs from the version installed with the workspace.
- An installed module has files missing.
- `SYSTEM.md` or `PRINCIPLES.md` does not say `status: approved`.
- A workflow `CONTEXT.md` has 80 lines or more (keep stage files under 80).
- A workflow `CONTEXT.md` still contains `<fill in: ...>` parts.
- `lessons/active.md` (from the staged-learning module) has more than 20 lessons.
- A file in `knowledge/` was last verified more than 90 days ago, or its `last_verified` date is not a date or lies in the future. With the knowledge-inbox module installed, a knowledge file without a date is listed as a note (INFO).

**Notes**

- A proposal with status `proposed` or `deferred` is waiting for your review.

## Example scenarios

- After setup, you run it and see only the two draft warnings. You approve both files and the warnings go away.
- You create a workflow with [new-workflow](workflow-generator.md) and forget two blanks. `doctor` says how many `<fill in: ...>` parts remain.
- You paste a file from the demo into `knowledge/`. `doctor` reports it as an error.

## What changes inside the system when it runs?

Nothing in your workspace. It only reads. A test runs it on a fresh workspace and checks that every file is byte-for-byte the same afterwards.

It loads the review rules from `tools/review.py` in the Living System folder, not from the copy in your workspace.

## Where does the human keep control?

`doctor` only reports. It never fixes, deletes or approves anything. You decide what to do with each line.

## What can go wrong, and how do you undo it?

- **Nothing to undo.** It writes nothing.
- **It cannot prove your workspace is correct.** It looks at file structure. It does not check who approved something, whether a rule is wise, or whether an agent obeys. A clean result does not mean agents will behave.
- **It does not look at everything.** For example, it does not read the handover note, and it does not detect a decision that was edited by hand.
- **Demo detection** compares your files with the `demo/` folder of the Living System copy it runs from.
- **A top-level `REFUSED`** means the tool could not start. Read the message. For a damaged manifest, restore `.living/manifest.json` from a backup or Git.

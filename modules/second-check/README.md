# Feature: second check

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `second-check`.

## What does this feature do?

It adds a three-step workflow for important work: one agent session makes it, a fresh session (ideally a different agent) checks it against a fixed checklist, and you decide. There are at most two correction rounds unless you say otherwise.

## Why would someone need it?

An AI that checks its own work tends to agree with itself. A second, independent look catches made-up facts, promises nobody agreed to, and conflicts with your rules, before the work reaches a client or your team.

## What problem does it solve?

- Mistakes are found before the work is used, not after.
- The check is the same every time, because it follows a written checklist.
- Endless rework is avoided: two rounds, then you decide.

## What does it require?

A Living System workspace. One agent is enough (use a fresh session for the check); two different agents, such as Claude Code and Codex, are better. No other modules.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace second-check          # shows what would be added
python3 tools/living.py add ~/my-workspace second-check --apply  # adds it
```

## How do you use it?

1. In one session: "Run stage 1 of the second-check workflow. Brief: ..."
2. Open a **new** session, ideally in the other agent: "Run stage 2 of the second-check workflow. Brief: ..." (the same brief).
3. Read the check. If it asks for changes, run stage 1 again with the check, then stage 2 again.
4. "Run stage 3": the agent summarises, and you decide.

## Example scenarios

- A proposal for a new client: Claude Code drafts it, Codex checks it, and finds a delivery date nobody agreed to.
- A summary of a long contract: the check confirms every point is traceable to a page, or marks it "not recorded".
- A plan for your team: the check finds it conflicts with your rule on who approves budgets, and names the decision.

## What changes inside the system when it runs?

Each stage writes one file into its own `output/` folder in `workflows/second-check/`. Nothing else changes. Installing adds the folder, the checklist and one routing row.

## Where does the human keep control?

- You start each stage.
- The checker only reports; it never edits the work.
- You decide what happens with the work, and nothing is ever sent by the workflow.

## What can go wrong, and how do you undo it?

- **The checker saw the maker's conversation:** it was not independent. Run stage 2 again in a new session.
- **The checklist does not fit your work:** edit `references/checklist.md`; it is yours.
- **Remove it:** `python3 tools/living.py remove ~/my-workspace second-check --apply`. Files you edited are kept.
- **Limits:** two agents can still both miss the same mistake. The check makes errors less likely; it does not guarantee correct work.

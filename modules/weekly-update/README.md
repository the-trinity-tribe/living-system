# Feature: weekly update workflow

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `weekly-update`.

## What does this feature do?

It adds a three-step workflow for writing a short weekly update: gather the facts, draft the update, then check who must approve it. Your AI agent does one step at a time and stops so you can check the result.

## Why would someone need it?

Weekly updates repeat every week, but each one still takes time, and it is easy to promise something you never agreed to. This keeps the update short, factual and checked.

## What problem does it solve?

- You no longer explain the update format every week; it lives in one file.
- The agent can only use facts from your files, so it cannot make things up silently.
- Who approves sending comes from your approved decisions, not from the agent's guess.

## What does it require?

A Living System workspace (made with `tools/living.py init`). No other modules. Claude Code or Codex to run the steps.

## How do you install or enable it?

From the Living System folder:

```sh
python3 tools/living.py add ~/my-workspace weekly-update          # shows what would be added
python3 tools/living.py add ~/my-workspace weekly-update --apply  # adds it
```

## How do you use it?

Open your workspace in Claude Code or Codex and say: "Run stage 1 of the weekly update for <project>." Check the facts list, edit it if needed, then ask for stage 2, then stage 3. You send the update yourself.

## Example scenarios

- A freelancer sends a Friday update to a client.
- An employee writes a status update for their manager.
- A student summarises a week of a group project for their supervisor.

## What changes inside the system when it runs?

Each stage writes one file into its own `output/` folder in `workflows/weekly-update/`. Nothing else changes. Installing adds the folder and one row under "Installed modules" in `CONTEXT-ROUTING.md`.

## Where does the human keep control?

- After every stage: you read, edit or stop.
- Stage 3 never decides who approves; it reads your decisions or asks you.
- Nothing is ever sent by the workflow.

## What can go wrong, and how do you undo it?

- **The facts are thin:** stage 1 lists what is "not recorded". Add notes to your project file and run it again.
- **No decision says who approves:** stage 3 says so. You decide, and can ask for a proposal to make it a rule.
- **Remove it:** `python3 tools/living.py remove ~/my-workspace weekly-update --apply`. Files you edited are kept; your decisions, proposals and projects are never touched.
- **Limits:** instructions guide the agent but cannot force it. Always read the draft before sending.

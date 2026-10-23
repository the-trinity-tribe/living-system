# Feature: staged learning

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `staged-learning`.

## What does this feature do?

It gives your agent a place to suggest lessons from its own mistakes, and gives you a short list of approved lessons the agent must follow next time.

## Why would someone need it?

AI sessions forget. You correct the same mistake again and again. This keeps the correction, but only after you agree with it.

## What problem does it solve?

- Less repeating yourself: an approved lesson is read at the start of real work, in any later session and by any supported agent.
- No silent self-change: the agent can only suggest; you decide what sticks.
- No bloat: at most 20 active lessons.

## What does it require?

A Living System workspace. No other modules.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace staged-learning          # shows what would be added
python3 tools/living.py add ~/my-workspace staged-learning --apply  # adds it
```

## How do you use it?

Work as usual. When the agent adds a suggestion to `lessons/inbox.md`, it tells you. Now and then, read the inbox: move good lessons to `lessons/active.md` yourself, or ask the agent to move one you name. Delete the rest.

## Example scenarios

- You told the agent twice to keep replies short. It suggests the lesson "Answer in at most five bullets." You approve it.
- A command failed the same way twice. The agent suggests the working command as a lesson.
- A suggestion would change who approves invoices. That is a rule, so the agent writes a proposal instead of a lesson.

## What changes inside the system when it runs?

Only `lessons/inbox.md` (agent suggestions) and `lessons/active.md` (your approvals) change. Installing adds the `lessons/` folder and two routing rows.

## Where does the human keep control?

- Only you move a lesson into the active list.
- Lessons can never override a decision.
- You can delete any lesson at any time.

## What can go wrong, and how do you undo it?

- **A bad lesson was approved:** delete it from `active.md`.
- **The inbox grows:** delete what you do not want; nothing in the inbox is in force.
- **Remove it:** `python3 tools/living.py remove ~/my-workspace staged-learning --apply`. Lesson files you edited are kept.
- **Limits:** the 20-lesson limit and "only you approve" are instructions; the agent can still ignore them. A later `doctor` check is planned to warn about a list that is too long.

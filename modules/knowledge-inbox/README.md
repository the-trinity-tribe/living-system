# Feature: knowledge inbox

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `knowledge-inbox`.

## What does this feature do?

It gives your agent a place to suggest knowledge worth keeping, such as a useful source or a research finding, and gives you a simple way to keep only what you approve. Every kept file records when it was last checked, and `doctor` reminds you when it is getting old.

## Why would someone need it?

Useful knowledge gets lost in chats, or it stays around long after it stopped being true. Both cost time, and outdated facts can quietly lead to wrong answers.

## What problem does it solve?

- Good sources and findings are kept in one place, with where they came from.
- The agent cannot quietly add "facts": it can only suggest them.
- Old knowledge is flagged for a re-check instead of being trusted forever.

## What does it require?

A Living System workspace. No other modules.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace knowledge-inbox          # shows what would be added
python3 tools/living.py add ~/my-workspace knowledge-inbox --apply  # adds it
```

## How do you use it?

Work as usual. When the agent adds a suggestion to `knowledge/inbox.md`, it tells you. Now and then, read the inbox: keep an item by turning it into `knowledge/<topic>.md` from `_template.md` with today's `last_verified` date (or ask the agent to do that for the item you name), and delete the rest. When `doctor` says a file is old, check it and update its date. You can mark how sure a file is with `confidence: low`, `medium` or `high` in its front matter. When a file is outdated or wrong, compost it: `python3 tools/living.py compost ~/my-workspace knowledge/<file>.md --reason "..."` moves it to `knowledge/archive/` with the date and reason, out of daily use but kept as history.

## Example scenarios

- You share an article about invoicing rules in your country. The agent suggests the key point, with the link, in the inbox. You keep it as `knowledge/invoicing.md`.
- Half a year later, `doctor` warns that `knowledge/invoicing.md` was last verified 190 days ago. You check the source again and update the date.
- A finding would change who approves invoices. That is a rule, so the agent writes a proposal instead.

## What changes inside the system when it runs?

The agent only appends to `knowledge/inbox.md`. Kept items become files in `knowledge/` with a `last_verified` date. `doctor` reads those dates; `status` shows how many suggestions wait and how many files are due for a re-check. Installing adds `knowledge/README.md`, `knowledge/inbox.md`, `knowledge/_template.md` and two routing rows.

## Where does the human keep control?

- Only you decide what moves from the inbox into `knowledge/`.
- Only a human check may change a `last_verified` date.
- Knowledge never overrides a decision.

## What can go wrong, and how do you undo it?

- **The inbox grows:** delete what you do not want; nothing in it is in use.
- **A date was changed without a real check:** set it back, or to the date you actually checked.
- **Remove it:** `python3 tools/living.py remove ~/my-workspace knowledge-inbox --apply`. Your own knowledge files stay; files you edited are kept.
- **Limits:** the 90-day reminder is a fixed rule of thumb, and "only you approve" is an instruction to the agent, not a lock.

# Feature: onboarding path

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

It gives a person a private reading path through what matters for their work, and the agent introduces it a few items at a time. The order is:

1. Company rules (when the workspace is linked to a company workspace).
2. How the company works (its approved `SYSTEM.md` and `PRINCIPLES.md`).
3. What earlier people in the same role handed on.
4. Company workflows.
5. Your own rules, your workflows and your approved lessons.

When a rule changes, the new version comes back on the path by itself.

## Why would someone need it?

A new person usually gets either everything at once (and remembers little) or nothing (and learns by mistakes). A short, ordered path, in small steps, is easier, especially for someone who is overwhelmed by long documents.

## What problem does it solve?

- New people learn the rules that apply before they need them.
- Nobody has to write an onboarding plan by hand: it comes from the rules and role knowledge that already exist.
- After a rule changes, everyone who already read the old one sees the new one.

## What does it require?

A Living System workspace and Python 3.10 or newer. Company items need a [connected workspace](connected-workspaces.md).

## How do you install or enable it?

Nothing to install. Ask your agent "What should I know?" or "What's next on my onboarding?". Or run:

```sh
python3 tools/living.py onboard ~/my-workspace
```

## How do you use it?

- The agent explains at most three items per session, in plain words, and asks whether each is clear.
- When you have understood one, it ticks it (or you tick the box in `me/onboarding.md`, or run `living.py onboard . --done <id>`).
- `status` reminds you how many items are left.

## Example scenarios

- A new account manager links their workspace to the company. The path starts with the company's three rules, then the team's notes on Q4 client questions, then the weekly update workflow.
- The rule on discounts is replaced while you are away. Next time, the new rule is back on your path, unticked.
- A student uses it alone: the path lists their own rules and workflows, as a weekly reminder of what they decided.

## What changes inside the system when it runs?

`onboard` writes `me/onboarding.md`: a checklist with one line per item. It keeps your ticks, adds new items and drops items that no longer apply. It writes only when something changed. Nothing else is touched.

## Where does the human keep control?

- The path is private (in `me/`; for employees that folder stays out of shared repositories) and is not a rule.
- You decide when you have understood something. The agent never grades you or keeps notes about how you did.
- You can skip, untick or delete the file at any time.

## What can go wrong, and how do you undo it?

- **Too much at once?** Say "only one item per day". The agent follows it.
- **An item no longer makes sense?** It disappears when the rule or file it points to is no longer current.
- **Start again:** delete `me/onboarding.md`; the next `onboard` makes a fresh one.

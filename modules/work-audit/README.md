# Feature: Work audit

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `work-audit`.

## What does this feature do?

Look at how work really happens before adding AI: map it, find friction, sort what to drop, keep, support or automate, then test one small change. It is a staged workflow with a stop for you after each step: map the work, find friction, sort the work, plan one small experiment, review the result.

## Why would someone need it?

So that the human sees how work really happens, removes what is unnecessary first, keeps human judgement where it matters, and tries one small, measured change before anything bigger.

## What problem does it solve?

- AI gets added to work that should not exist at all.
- Human judgement gets automated away by accident.
- Big changes are made without a small test first.

## What does it require?

A Living System workspace, Python 3.10 or newer, and Claude Code or Codex.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace work-audit
python3 tools/living.py add ~/my-workspace work-audit --apply
```

## How do you use it?

Ask your agent in your own words (for example "where do we lose time"). It follows `workflows/work-audit/CONTEXT.md`, one stage at a time, and saves each stage's result in that stage's `output/` folder.

## Example scenarios

- A small job-placement office maps its week, finds that the same programme rules are explained to every new client, and tests a one-page handout for two weeks before thinking about AI.
- A freelancer sorts their admin: two reports nobody reads are dropped; invoicing gets a checklist.

## What changes inside the system when it runs?

Files are written only inside `workflows/work-audit/`. No rule changes; anything that should become a rule is drafted as a proposal for you to review.

## Where does the human keep control?

You confirm every stage. These always need your yes: starting the experiment; any rule that comes out of it (as a proposal); sharing the audit with others.

## What can go wrong, and how do you undo it?

- **Numbers that were not measured.** The module asks for measurements; anything else is labelled as an estimate.
- **Personal judgements about colleagues.** Use roles and work, never people's performance.
- Remove the module with `living.py remove`; files you edited are kept.

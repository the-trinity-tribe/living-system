# Feature: Research review

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `research-review`.

## What does this feature do?

Answer a question from sources: every claim points to a dated source, conflicts and gaps are listed, nothing is filled in by guessing. It is a staged workflow with a stop for you after each step: frame the question, collect sources, check claims against sources, name the gaps, summarise.

## Why would someone need it?

So that a question is answered from sources the human can check, with what is known, what conflicts and what is still unknown kept apart.

## What problem does it solve?

- Answers that sound right but have no source.
- Conflicting evidence that quietly disappears.
- Gaps filled with guesses.

## What does it require?

A Living System workspace, Python 3.10 or newer, and Claude Code or Codex.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace research-review
python3 tools/living.py add ~/my-workspace research-review --apply
```

## How do you use it?

Ask your agent in your own words (for example "research this"). It follows `workflows/research-review/CONTEXT.md`, one stage at a time, and saves each stage's result in that stage's `output/` folder.

## Example scenarios

- "Is a four-day week better for small teams?": the review lists studies with dates, notes which were run by interested parties, and ends with what is still unknown.
- Checking a claim a client made before you repeat it.

## What changes inside the system when it runs?

Files are written only inside `workflows/research-review/`. No rule changes; anything that should become a rule is drafted as a proposal for you to review.

## Where does the human keep control?

You confirm every stage. These always need your yes: using or sharing the summary; treating any finding as a rule (as a proposal).

## What can go wrong, and how do you undo it?

- **An agent invents a source.** The rules forbid it; still open important sources yourself. For important use, have it checked by a fresh session.
- **Old sources.** Each source has a date; agree how recent it must be.
- Remove the module with `living.py remove`; files you edited are kept.

# Feature: Small experiment

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `small-experiment`.

## What does this feature do?

Try one change and see honestly what happened: a starting point, one versioned change, measures kept apart by kind, and a review that keeps, revises or reverts it. It is a staged workflow with a stop for you after each step: set the starting point, run the change, measure the same way, review and decide.

## Why would someone need it?

So that one change is tried for a set time, measured the same way before and after, and judged on what was actually seen, without claiming more than the data shows.

## What problem does it solve?

- Changes kept or dropped on a feeling.
- One number standing in for everything that matters.
- Results claimed as proof when they are one observation.

## What does it require?

A Living System workspace, Python 3.10 or newer, and Claude Code or Codex.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace small-experiment
python3 tools/living.py add ~/my-workspace small-experiment --apply
```

## How do you use it?

Ask your agent in your own words (for example "does this actually help"). It follows `workflows/small-experiment/CONTEXT.md`, one stage at a time, and saves each stage's result in that stage's `output/` folder.

## Example scenarios

- A coach tries sending a one-page summary after each session for three weeks: offers sent stay the same, clients' questions by e-mail halve (counted), and the coach rates feeling in control higher. Kept, with the limits written down.
- A team tries a shared checklist for client onboarding; errors found later do not change, extra time is spent. Reverted.

## What changes inside the system when it runs?

Files are written only inside `workflows/small-experiment/`. No rule changes; anything that should become a rule is drafted as a proposal for you to review.

## Where does the human keep control?

You confirm every stage. These always need your yes: starting the experiment; changing what or how you measure midway; any rule that comes out of it (as a proposal); sharing the results.

## What can go wrong, and how do you undo it?

- **Reading too much into it.** The review states how few times it ran and what else changed; it never says the change caused the result.
- **Measuring people.** Measures about a person's experience are reported by that person, never inferred.
- Remove the module with `living.py remove`; files you edited are kept.

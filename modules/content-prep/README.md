# Feature: Content preparation

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `content-prep`.

## What does this feature do?

Prepare a post, article or newsletter in checked steps: brief, draft, fact and tone check, ready for you to publish. It is a staged workflow with a stop for you after each step: write the brief, draft, check facts and tone, ready for the human.

## Why would someone need it?

So that content is prepared from a clear brief, checked for facts and tone by someone who did not write it, and handed to the human to publish.

## What problem does it solve?

- Posts with claims nobody can back up.
- Tone that does not fit the audience.
- Writing and checking by the same person in the same breath.

## What does it require?

A Living System workspace, Python 3.10 or newer, and Claude Code or Codex.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace content-prep
python3 tools/living.py add ~/my-workspace content-prep --apply
```

## How do you use it?

Ask your agent in your own words (for example "write a post"). It follows `workflows/content-prep/CONTEXT.md`, one stage at a time, and saves each stage's result in that stage's `output/` folder.

## Example scenarios

- A monthly newsletter: brief with three facts and their sources, a draft, a fresh-session check that removes one unsupported claim, then ready for you.
- A LinkedIn post about a project, checked for promises you cannot keep.

## What changes inside the system when it runs?

Files are written only inside `workflows/content-prep/`. No rule changes; anything that should become a rule is drafted as a proposal for you to review.

## Where does the human keep control?

You confirm every stage. These always need your yes: publishing or sending; any claim that has no source.

## What can go wrong, and how do you undo it?

- **An unsupported claim slips through.** The check marks claims without sources; you confirm the rest.
- **Too formal or too casual.** Put the tone in the brief; the check looks for it.
- Remove the module with `living.py remove`; files you edited are kept.

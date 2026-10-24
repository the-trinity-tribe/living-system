# Workflow: content preparation

Staged workflow in the style of Interpretable Context Methodology (ICM). Working context, not authority. It cannot change any rule.

Goal: content is prepared from a clear brief, checked for facts and tone by someone who did not write it, and handed to the human to publish.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-brief/` | Write the brief | `01-brief/output/` |
| 2 | `02-draft/` | Draft | `02-draft/output/` |
| 3 | `03-check/` | Check facts and tone | `03-check/output/` |
| 4 | `04-ready/` | Ready for the human | `04-ready/output/` |

After each stage the human checks the result before the next one starts.

## Decisions that apply

- All current decisions (`python3 tools/review.py current`). Flag anything that conflicts with one.

## Never do

- Never publish, post or send; the human does.
- Never invent facts, numbers, quotes or testimonials.
- Never present a guess as a measured result.
- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.

## Shared reference

- `references/check.md`

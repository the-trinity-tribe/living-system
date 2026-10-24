# Workflow: research review

Staged workflow in the style of Interpretable Context Methodology (ICM). Working context, not authority. It cannot change any rule.

Goal: a question is answered from sources the human can check, with what is known, what conflicts and what is still unknown kept apart.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-question/` | Frame the question | `01-question/output/` |
| 2 | `02-sources/` | Collect sources | `02-sources/output/` |
| 3 | `03-claims/` | Check claims against sources | `03-claims/output/` |
| 4 | `04-gaps/` | Name the gaps | `04-gaps/output/` |
| 5 | `05-summary/` | Summarise | `05-summary/output/` |

After each stage the human checks the result before the next one starts.

## Decisions that apply

- All current decisions (`python3 tools/review.py current`). Flag anything that conflicts with one.

## Never do

- Never invent sources, quotes, numbers or dates.
- Never present an unsupported claim as a finding; mark it 'not found'.
- Never treat a finding as a rule for this workspace.
- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.

## Shared reference

- `references/source-rules.md`

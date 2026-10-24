# Workflow: work audit

Staged workflow in the style of Interpretable Context Methodology (ICM). Working context, not authority. It cannot change any rule.

Goal: the human sees how work really happens, removes what is unnecessary first, keeps human judgement where it matters, and tries one small, measured change before anything bigger.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-map/` | Map the work | `01-map/output/` |
| 2 | `02-friction/` | Find friction | `02-friction/output/` |
| 3 | `03-sort/` | Sort the work | `03-sort/output/` |
| 4 | `04-experiment/` | Plan one small experiment | `04-experiment/output/` |
| 5 | `05-review/` | Review the result | `05-review/output/` |

After each stage the human checks the result before the next one starts.

## Decisions that apply

- All current decisions (`python3 tools/review.py current`). Flag anything that conflicts with one.

## Never do

- Never invent time or money savings. Only measured numbers, labelled as such.
- Use roles, not names of people, in anything that may be shared.
- Never present an experiment's idea as a result.
- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.

## Shared reference

- `references/questions.md`

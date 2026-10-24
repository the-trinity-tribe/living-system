# Workflow: small experiment

Staged workflow in the style of Interpretable Context Methodology (ICM). Working context, not authority. It cannot change any rule.

Goal: one change is tried for a set time, measured the same way before and after, and judged on what was actually seen, without claiming more than the data shows.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-baseline/` | Set the starting point | `01-baseline/output/` |
| 2 | `02-change/` | Run the change | `02-change/output/` |
| 3 | `03-measure/` | Measure the same way | `03-measure/output/` |
| 4 | `04-review/` | Review and decide | `04-review/output/` |

After each stage the human checks the result before the next one starts.

## Decisions that apply

- All current decisions (`python3 tools/review.py current`). Flag anything that conflicts with one.

## Never do

- Never claim the change caused a result; say what was seen, how often, and what else changed at the same time.
- Never add made-up numbers; 'not measured' is an answer.
- Never measure people's performance or wellbeing without their own say; measures about a person are reported by that person.
- Never change the measure midway without writing down what changed and why.
- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.

## Shared reference

- `references/experiment-card.md`

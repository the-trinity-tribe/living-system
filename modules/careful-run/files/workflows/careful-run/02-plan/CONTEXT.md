# Stage 2: plan

Plan the steps, the checks and the way back.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Card | `../runs/<card>` | All | Goal and scope |
| Profiles | `../references/profiles.md` | Matching section | Extra checks |
| Current decisions | output of `python3 tools/review.py current` | Rule, Scope | Rules the plan must follow |

## Process

1. Fill in Plan, Who does what, How to undo and Verify with.
2. List every file in scope under Files in scope.
3. For high risk, show the plan as an approval screen (what, why, risk, cost, undo).
4. Set `Stage: 2-plan`.

## Outputs

The updated card

## Checkpoint

High risk: the human says yes to the plan. Low risk: the human may go ahead.

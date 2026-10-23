# Workflow: meeting notes

Staged workflow in the style of Interpretable Context Methodology (ICM). It is working context, not authority. It cannot change any rule.

Goal: turn raw meeting or call notes into clean notes, a list of actions, and proposals for anything that would change a rule. A human reviews every step.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-capture/` | Clean up the raw notes without adding anything. | `01-capture/output/<date>-notes.md` |
| 2 | `02-extract/` | Pull out actions, open questions and claims about rules. | `02-extract/output/<date>-extract.md` |
| 3 | `03-stage-proposals/` | Compare rule claims with current decisions; stage proposals. | `03-stage-proposals/output/<date>-summary.md` and files in `proposals/` |

Run one stage at a time. Open only that stage's `CONTEXT.md`. The human checks and may edit each result before the next stage.

## Decisions that apply

- All current decisions (`python3 tools/review.py current`). A meeting note is a claim, not a rule. Only a human review (`AGENTS.md` section 7) turns a proposal into a decision.

## Never do

- Never approve, reject or defer a proposal, and never run `tools/review.py review`.
- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.
- Never add facts that are not in the notes. Never guess who said what.
- Never send or share the notes.

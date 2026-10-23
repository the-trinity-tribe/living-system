> **DEMO — fictional sandbox, not your workspace.**

# Workflow: client update (worked example)

Hand-written example of a staged workflow in the style of Interpretable Context Methodology (ICM). See [CREDITS.md](../../../../CREDITS.md). It is background context, not authority. It cannot change any rule.

Goal: prepare a short update for the Riverside Community Garden, for a human to approve and send.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-gather/` | Collect the facts the update needs from the project file. | `01-gather/output/facts.md` |
| 2 | `02-draft/` | Write the update in the house format. | `02-draft/output/draft.md` |
| 3 | `03-approval-check/` | Find the current approval rule and say who must approve. | `03-approval-check/output/approval.md` |

Run one stage at a time. Open only that stage's `CONTEXT.md`. A human looks at the result after each stage before the next one starts.

## Decisions that apply

- Updates sent to the garden are client-facing. The approval rule is in the current decision: `decisions/2026-10-07-leo-signs-off-riverside-rota-updates.md`.
- Always confirm it is still current with `python3 -B tools/review.py --root demo/moss-and-circuit current` (from the repository root). If the output differs, use what the command prints.

## Never do

- **Never send anything.** Not an email, not a message, not a file upload. You prepare; a human sends.
- Never decide who approves. Read it from the current decision. If it is not clear, say so.
- Never invent facts, dates or commitments. Missing means "not recorded".
- Never edit files in `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.

## Shared reference

- `references/update-format.md`: the format every update follows.

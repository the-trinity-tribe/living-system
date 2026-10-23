# Workflow: weekly update

Staged workflow in the style of Interpretable Context Methodology (ICM). It is working context, not authority. It cannot change any rule.

Goal: a short weekly update (for a client, a team, a manager or yourself) that a human approves and sends.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-gather/` | Collect this week's facts from your files. | `01-gather/output/<date>-facts.md` |
| 2 | `02-draft/` | Write the update in the shared format. | `02-draft/output/<date>-draft.md` |
| 3 | `03-approval-check/` | Find who must approve it before it is sent. | `03-approval-check/output/<date>-approval.md` |

Run one stage at a time. Open only that stage's `CONTEXT.md`. The human looks at the result after each stage and may edit it before the next stage starts. The next stage uses the edited file.

## Decisions that apply

- Whatever the current decisions say about who approves outgoing work. Stage 3 finds them with `python3 tools/review.py current`.
- If no current decision covers this update, nothing is approved yet: the human decides, and may ask for a `kind: new` proposal (see `AGENTS.md` section 6b) to make it a standing rule.

## Never do

- **Never send anything.** You prepare; a human sends.
- Never decide who approves. Read it from a current decision, or ask.
- Never invent facts, dates, numbers or commitments. Missing means "not recorded".
- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.

## Shared reference

- `references/update-format.md`: the format every update follows. Edit it to suit your audience.

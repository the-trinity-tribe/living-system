# Stage 3: decide

Help the human decide. The decision is theirs.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Work | the newest file in `01-make/output/` | All | What would be used |
| Check | the newest file in `02-check/output/` | All | What the checker found |

## Process

1. Summarise the verdict and any open points in at most five lines.
2. Ask the human: use it as it is, use it after their own edits, run another round, or drop it.
3. If a point would change a rule, offer a proposal instead (`AGENTS.md` section 6).
4. Write down what the human decided.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Decision note | `03-decide/output/<date>-decision.md` | Markdown: the human's choice and why, in their words |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 4 | The decision note | Nothing more; a human uses or sends the work, outside this workflow |

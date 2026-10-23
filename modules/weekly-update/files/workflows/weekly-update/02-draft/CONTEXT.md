# Stage 2: draft

Write the update from the facts list only.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Facts | the newest file in `01-gather/output/` | All, as the human edited it | The only allowed content |
| Format | `../references/update-format.md` | All | The shape of every update |

## Process

1. Read the facts list. Use nothing that is not in it.
2. Write the four parts of the format.
3. Leave the sign-off as `(approver: set in stage 3)`.
4. Count words. If over the limit in the format, cut.
5. Mark any sentence that depends on a "not recorded" item with `[CHECK]`.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Draft update | `02-draft/output/<date>-draft.md` | Markdown, in the format, no sending details |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 5 | The draft and its `[CHECK]` marks | Edit, accept, or go back to stage 1 |

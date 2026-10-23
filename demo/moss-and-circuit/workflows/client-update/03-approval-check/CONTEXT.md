# Stage 3: approval check

Say who must approve this update before it is sent. Do not send it.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Draft | `02-draft/output/draft.md` | All | What would be sent |
| Current decisions | output of `review.py current` | The printed list | Shows which decision is current |
| Current decision | the file the command printed | Sections "Rule" and "Exception" | Who may approve what |

## Process

1. Run `python3 -B tools/review.py --root demo/moss-and-circuit current` (from the repository root). Note the file it prints.
2. Read that decision's "Rule" and "Exception". Do not use a file the command did not print.
3. Decide which case the draft is: a routine schedule update (such as a revised rota), or anything else. If the draft contains pricing, unusual commitments, or anything that could affect the studio's reputation, it is **not** routine.
4. Write who must approve before sending, quote the sentence from the decision, and name the file.
5. If the case is unclear, write "unclear" and ask the human. Do not choose.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Approval note | `03-approval-check/output/approval.md` | Markdown: case, required approver, quoted sentence, decision file |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 5 | The approval note | Whether it is right. The named approver reads the draft and decides. A human sends it, outside this workflow |

# Stage 3: approval check

Say who must approve this update before it is sent. Do not send it.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Draft | the newest file in `02-draft/output/` | All | What would be sent |
| Current decisions | output of `python3 tools/review.py current` | The printed list | Which rules are current |
| Each current decision | the files the command printed | Sections "Rule", "Exception", "Scope" | Who may approve what |

## Process

1. Run `python3 tools/review.py current`. Use only the files it prints.
2. Find a decision that covers this kind of update for this audience.
3. If one covers it: write the required approver, quote the sentence, and name the file.
4. If none covers it: write "No current decision covers this. You decide." Offer to draft a `kind: new` proposal if the human wants a standing rule.
5. If the case is unclear, write "unclear" and ask. Do not choose.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Approval note | `03-approval-check/output/<date>-approval.md` | Markdown: required approver or "no decision", quoted sentence, decision file |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 5 | The approval note | Whether it is right. The approver reads the draft. A human sends it, outside this workflow |

# Stage 3: stage proposals

Compare each claim about a rule with the current decisions. Stage a proposal where one is needed. Approve nothing.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Extract | the newest file in `02-extract/output/` | "Claims about rules" only | What to compare |
| Current decisions | output of `python3 tools/review.py current`, then those files | Rule, Exception, Scope | The rules in force |
| Pending proposals | `proposals/` | Files with `status: proposed` | Avoid duplicates |
| Proposal format | `AGENTS.md` sections 6, 6a and 6b | All | How to write a proposal |

## Process

1. For each claim, decide: already the rule / conflicts with or changes a current decision / a new rule no decision covers / not a rule.
2. Skip a claim if a `proposed` proposal already covers the same change. Name that file instead.
3. Changes a decision: write a section 6a proposal. Get `target_sha256` with `python3 tools/review.py hash <decision file>`.
4. New rule: write a section 6b proposal (`kind: new`, `target: none`).
5. Write the narrowest reading the note supports. Put broader readings under open questions. Say the attribution is not verified.
6. Run `python3 tools/review.py check`; fix any problem in the files you wrote.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Summary | `03-stage-proposals/output/<date>-summary.md` | Markdown: each claim, its category, and the proposal file if any |
| Proposals | `proposals/YYYY-MM-DD-short-name.md` | As in `AGENTS.md` section 6 |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 6 | The summary and the new proposal files | Review each proposal with `tools/review.py review`, or leave them pending |

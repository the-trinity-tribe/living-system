# Stage 2: check

Check the work. Do not edit it. Run this in a **fresh session** that did not make the work, ideally with a different agent.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Human | The same brief | All | What was asked |
| Work | the newest file in `01-make/output/` | All | What to check |
| Checklist | `../references/checklist.md` | All | What every check covers |
| Current decisions | output of `python3 tools/review.py current`, then those files | Rule, Exception, Scope | Rules the work must follow |

## Process

1. Read only the inputs above, not the maker's conversation.
2. Go through every checklist line. For each: pass, or what is wrong and where.
3. Give one verdict: **approved**, **request changes** (with a numbered list), or **blocked** (it cannot be fixed by small changes, or it conflicts with a decision; say which).
4. Note which correction round this is (1 or 2).

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Check report | `02-check/output/<date>-check.md` | Markdown: checklist results, verdict, "Changes needed", round number |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 4 | The verdict and the list | Go to stage 3, or run another round (at most two without asking) |

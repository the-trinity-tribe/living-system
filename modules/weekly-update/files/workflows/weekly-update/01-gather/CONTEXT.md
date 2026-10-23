# Stage 1: gather

Collect the facts this week's update needs. Write nothing else.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Human | The request | Who the update is for, and which project or period | Sets the scope |
| Projects | The relevant file in `projects/` | Working notes from this period | What happened |
| Handover | `handover/LATEST.md` | All | Where the last session stopped |
| Current decisions | output of `python3 tools/review.py current`, then those files | Rule, Exception and Scope sections | Rules that limit what can be said, and conflicts to flag |

## Process

1. Ask the human who the update is for and which project or period, if the request does not say.
2. Read the inputs. Do not read other folders.
3. List facts as bullets, each with the file it came from.
4. List what is **not recorded** but an update would normally need.
5. If a note conflicts with a current decision, list it under "Conflicts" and do not use it as a fact.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Facts list | `01-gather/output/<date>-facts.md` | Markdown: Facts (with sources), Not recorded, Conflicts |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 5 | The facts list and the "not recorded" gaps | Edit or fill gaps, then start stage 2, or stop |

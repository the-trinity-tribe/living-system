# Stage 1: make

Make the work from the brief. On a correction round, change only what the check asked for.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Human | The brief: what, for whom, by when | All | The only task |
| Previous check | the newest file in `02-check/output/`, on a correction round only | "Changes needed" | What to fix |
| Context | Files the brief names, and current decisions | As needed | Facts and rules |

## Process

1. Restate the brief in two lines and ask if anything is unclear.
2. Make the work. Mark anything not recorded as "not recorded".
3. On a correction round, fix each listed point and note how.
4. List the files you used.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| The work | `01-make/output/<date>-work.md` | Markdown, with "Sources used" and, on a correction round, "Changes made" |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 4 | The work | Start stage 2 in a fresh session, or stop |

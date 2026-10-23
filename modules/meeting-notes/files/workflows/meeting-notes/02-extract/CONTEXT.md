# Stage 2: extract

Pull out what needs follow-up.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Notes | the newest file in `01-capture/output/` | All, as the human edited it | The only allowed content |

## Process

1. **Actions:** what, who, by when. Missing owner or date means "not recorded".
2. **Open questions:** anything left undecided.
3. **Claims about rules:** any sentence saying who may, must or must not do something, or how something must be done. Quote it and name the speaker as recorded.
4. Add nothing that is not in the notes.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Extract | `02-extract/output/<date>-extract.md` | Markdown: Actions, Open questions, Claims about rules (quoted) |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 4 | The three lists | Correct them, then start stage 3, or stop |

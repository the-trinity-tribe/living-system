# Stage 6: hand back

Tell the human what was done and what is left.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Card | `../runs/<card>` | All | The run |
| Check and verify | newest files in `../04-check/output/` and `../05-verify/output/` | All | Evidence |

## Process

1. Write `output/<date>-hand-back.md`: what was done (with files), what was checked and verified, what is open, one next step.
2. Update `handover/LATEST.md`.
3. Set `Stage: 6-hand-back`.

## Outputs

`output/<date>-hand-back.md`

## Checkpoint

The human decides: use it, change it, or stop.

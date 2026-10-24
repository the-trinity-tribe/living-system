# Stage 6: hand back

Tell the human what was done and what is left.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Card | `../runs/<card>` | All | The run |
| Check and verify | the newest `<card-name>-check-*` and `<card-name>-verify-*` files | All | Evidence |

## Process

1. Write `output/<card-name>-hand-back.md`: what was done (with files), what was checked and verified, how far it got (planned, started, finished, output made, checked, delivered, reported), what is open, one next step.
2. Update `handover/LATEST.md`.
3. Set `Stage: 6-hand-back`.

## Outputs

`output/<card-name>-hand-back.md`

## Checkpoint

The human decides: use it, change it, or stop.

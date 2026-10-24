# Stage 5: verify

Run the checks named in the plan. Tools, not opinions.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Card | `../runs/<card>` | Verify with | Which checks |

## Process

1. Run each check. Copy its result (pass or fail, and the exact message on failure).
2. For high risk, also run `python3 <product folder>/tools/living.py doctor .`.
3. Say how far the work got, in these words: planned, started, finished, output made, checked, delivered (to where it was meant to go), reported to the human. 'Finished' is not 'delivered'.
4. Save the results as `output/<card-name>-verify-<round>.md`. Set `Stage: 5-verify`.

## Outputs

`output/<card-name>-verify-<round>.md`

## Checkpoint

All pass goes to hand back; any fail goes back to make.

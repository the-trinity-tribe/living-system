# Stage 5: verify

Run the checks named in the plan. Tools, not opinions.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Card | `../runs/<card>` | Verify with | Which checks |

## Process

1. Run each check. Copy its result (pass or fail, and the exact message on failure).
2. For high risk, also run `python3 <product folder>/tools/living.py doctor .`.
3. Save the results as `output/<date>-verify.md`. Set `Stage: 5-verify`.

## Outputs

`output/<date>-verify.md`

## Checkpoint

All pass goes to hand back; any fail goes back to make.

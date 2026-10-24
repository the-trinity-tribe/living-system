# Stage 4: check

Check the result against the card. Run this in a **fresh session** that did not make it, ideally another agent.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Card | `../runs/<card>` | All | What was promised |
| Profiles | `../references/profiles.md` | Matching section | Extra checks |
| The changed files | Files in scope | All | What to check |

## Process

1. Read only the inputs, not the maker's conversation.
2. For each Done-when line and profile check: pass, or what is wrong and where.
3. Give one verdict: approved, request changes (numbered), or blocked. Note the correction round.
4. Save it as `output/<date>-check.md`. Never edit the work.

## Outputs

`output/<date>-check.md`

## Checkpoint

Approved goes to verify; request changes goes back to make (at most two rounds).

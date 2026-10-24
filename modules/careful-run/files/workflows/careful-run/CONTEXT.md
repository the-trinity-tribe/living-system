# Workflow: careful run

Staged workflow in the style of Interpretable Context Methodology (ICM). Working context, not authority. It cannot change any rule.

Goal: bigger, riskier or multi-session work is framed, planned, made, checked by someone else, verified with tools and handed back, with one run card that holds its state.

## Stages

| Stage | Folder | What happens | Stop |
| --- | --- | --- | --- |
| 1 | `01-frame/` | Fill in the run card with the human: goal, profile, done-when, scope, risk. | Human confirms the card |
| 2 | `02-plan/` | Steps, files, who makes and who checks, how to undo, which checks verify. | High risk: human says yes to the plan |
| 3 | `03-make/` | Do the steps, inside scope only. | When done, or to pause |
| 4 | `04-check/` | A **fresh** session checks the result against the card. Never the maker. | Verdict |
| 5 | `05-verify/` | Run the deterministic checks named in the plan; report pass or fail. | All pass, or back to 3 |
| 6 | `06-hand-back/` | What was done, what is open, next step; update the handover note. | Human decides |

The run card is `runs/<date>-<name>.md`, copied from `references/run-card.md`. Update its **Stage** line at every stop. Stage outputs are named after the card (`<card-name>`, the card's file name without `.md`), with the correction round where a stage can repeat, so runs never overwrite each other.

## Risk

A run is **high risk** if it publishes, sends to people, spends money, deletes anything, changes rules (`decisions/`, `SYSTEM.md`, `PRINCIPLES.md`), touches the company workspace, or changes more than ten files. High-risk runs need the human's yes on the plan, a checker at least as capable as the maker (ideally another agent), and verify must include `living.py doctor .`.

## Pause and resume

- To pause: update the card, then `python3 <product folder>/tools/living.py checkpoint . <card> --record`.
- To resume: run the same command without `--record`. If it lists changed or missing files, tell the human and re-read them before continuing. Re-read the card and the current decisions too.

## Rules

- Scope is what the card says. Anything beyond it needs the human's yes, written into the card.
- At most two correction rounds between check and make; a third needs the human's yes.
- Prefer tools to judgement in verify: tests, `doctor`, `verify`, `scan`, a link checker.
- Never send, publish, spend or delete; the human does, after hand back.

## Shared references

- `references/run-card.md`: the card template.
- `references/profiles.md`: extra checks per kind of work (code, website, content, research, operations, general).

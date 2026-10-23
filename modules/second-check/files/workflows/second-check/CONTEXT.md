# Workflow: second check

Staged workflow in the style of Interpretable Context Methodology (ICM). It is working context, not authority. It cannot change any rule.

Goal: important work (a client proposal, a summary of a contract, a plan others will rely on) is made, then checked by someone who did not make it, then a human decides.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-make/` | Make the work from the human's brief. | `01-make/output/<date>-work.md` |
| 2 | `02-check/` | A **fresh** session checks it against the brief and the checklist. | `02-check/output/<date>-check.md` |
| 3 | `03-decide/` | The human reads both and decides. | `03-decide/output/<date>-decision.md` |

**The checker must not be the maker.** Run stage 2 in a new session, ideally with a different agent (for example Codex checks work made in Claude Code, or the other way round). The checker reads only the brief, the work and the checklist, not the maker's conversation.

At most **two correction rounds**: after a "request changes" verdict, stage 1 runs again with the checker's list, then stage 2 again. A third round needs the human's explicit yes.

## Decisions that apply

- All current decisions (`python3 tools/review.py current`). The checker flags any part of the work that conflicts with one.

## Never do

- Never send, publish or share the work. A human does that.
- The checker never edits the work; it only reports.
- Never invent facts, sources or commitments. Missing means "not recorded".
- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.

## Shared reference

- `references/checklist.md`: what every check covers. Add checks for your kind of work.

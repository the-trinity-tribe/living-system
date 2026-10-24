# Workflow: client intake

Staged workflow in the style of Interpretable Context Methodology (ICM). Working context, not authority. It cannot change any rule.

Goal: a new request becomes a short, checked picture: what the client asks for, what they need, what is unknown, and one proposed next step, without promising anything.

## Stages

| Stage | Folder | What happens | Output |
| --- | --- | --- | --- |
| 1 | `01-request/` | Write down the request | `01-request/output/` |
| 2 | `02-context/` | Fill in the picture | `02-context/output/` |
| 3 | `03-fit/` | Check the fit | `03-fit/output/` |
| 4 | `04-next-step/` | Propose a next step | `04-next-step/output/` |

After each stage the human checks the result before the next one starts.

## Decisions that apply

- All current decisions (`python3 tools/review.py current`). Flag anything that conflicts with one.

## Never do

- Never send, reply or promise anything; the human does.
- Never invent prices, dates or capacity.
- Keep contact details out of these files; use a short client code (for example client-a) and keep details in your mail or client system.
- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.

## Shared reference

- `references/intake-questions.md`

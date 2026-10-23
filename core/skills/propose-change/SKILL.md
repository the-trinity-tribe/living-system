---
name: propose-change
description: Turn a wish to add, change, replace or end a rule into a correctly formatted proposal for the human to review; never change a decision directly. Use when the human or a note says a rule should change, or asks to fix or update a decision.
---

Decisions change only through review (`AGENTS.md` sections 6 and 7). Never edit files in `decisions/`.

1. Find the current rule: `python3 tools/review.py current`, then read the decision. `python3 tools/review.py history` shows how it changed before.
2. Choose the kind: `new` (no rule yet), `exception` (keep the rule, add an exception), `replace` (a different rule), `retire` (no rule any more). If unsure between exception and replace, choose the narrower exception and say why.
3. Show it with `python3 <product folder>/tools/living.py propose . --kind <kind> --title "..." --rule "..." --evidence "..."` (add `--target decisions/<file>.md` for exception, replace and retire), without `--apply`. Write the narrowest reading of the evidence; put broader readings under open questions with `--why`.
4. After the human agrees to the wording, run it with `--apply` and show the review command it prints. The human decides.

---
name: tend
description: A calm upkeep pass through everything waiting in this Living System workspace, one item at a time (proposals, knowledge and lesson suggestions, shared role knowledge, stale knowledge, repeated work to decide, parked ideas). Use when the human says "tend", "let's tidy up", "what's piling up?" or has a few minutes for maintenance.
---

Upkeep, not a sprint. The human decides every item; you never approve, accept or delete on your own.

1. Ask how much time the human has (for example 10 minutes). Stop when it is used up.
2. Run `python3 <product folder>/tools/living.py status .`, `living.py park .` and `living.py doctor .` (on Windows: `py`). Make one list, in this order: rules waiting for review, shared role knowledge waiting, parked items whose date has come, knowledge and lesson suggestions, knowledge due for a re-check or marked low confidence, likely duplicate knowledge, delegations whose review date has come, repeated work to decide, other parked ideas.
3. Take **one** item. Say in two or three plain sentences what it is and what the choices are. For a proposal, show the review command it printed; run it only when the human names the proposal and states the outcome (`AGENTS.md` section 7).
4. Do what the human chose, with the matching command: `runs . --decide`, `park . --done N`, `role-review` (company workspace, and only when they say accept or reject), or editing a knowledge file's `last_verified` after they confirm it is still true. For a parked idea, offer the `idea-check` skill, keep it parked, or tick it off. For knowledge that is outdated or wrong, offer `living.py compost . <file> --reason "..."` (plan first). For duplicates, offer to merge them with the human. If an active lesson keeps being needed and would work better as a rule, offer to draft a proposal (`living.py propose`); never approve it.
5. Say what is left, then take the next item, or stop if the human wants to.
6. End with one line: what was done and what is left for next time.

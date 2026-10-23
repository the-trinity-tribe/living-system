---
name: living-status
description: Show what needs the human's attention in this Living System workspace (proposals to review, drafts to approve, repeated work to decide on, the last next step). Use when the human asks "what's pending", "what needs my attention" or starts a work session.
---

1. Find the Living System folder: `product_folder` in `.living/local.json`. If it is missing, ask the human.
2. Run `python3 <product folder>/tools/living.py status .` (on Windows: `py` instead of `python3`).
3. Tell the human the result in plain words, most important first. For each proposal waiting for review, say what it would change and show the review command it printed. Do not run that command yourself unless the human names the proposal and says "approve" (`AGENTS.md` section 7).
4. If nothing is waiting, say so in one line.

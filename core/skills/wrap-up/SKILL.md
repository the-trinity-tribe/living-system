---
name: wrap-up
description: End a work session in a Living System workspace by writing the handover note so the next session, with any agent, can continue. Use when the human says "wrap up", "let's stop here" or a piece of work is finished.
---

Follow `AGENTS.md` section 9.

1. Replace the text of `handover/LATEST.md` with: the date and what you worked on; what was done (with file names); what is still open; proposals waiting for review (file names); and one next step for the human. Facts point to files; this note is not a rule.
2. If the work was something that repeats, make sure it was counted (`AGENTS.md` section 11).
3. Run `python3 <product folder>/tools/living.py status .` and mention anything waiting, in one or two lines.

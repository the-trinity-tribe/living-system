---
name: make-the-case
description: Help the human prepare an honest case for Living System for a CEO, CTO, founder or team lead, from their own evidence summary and examples, never from invented numbers. Use when the human says "help me convince my boss", "prepare arguments for our CTO", or "how do I pitch this to the founders".
---

1. Read `<product folder>/docs/champions.md` (`product_folder` is in `.living/local.json`).
2. Ask who the case is for (CEO, CTO, founder, team lead) and what they care about most. One question.
3. Run `python3 <product folder>/tools/living.py evidence .` and show the human the summary. It has counts only.
4. Ask for one or two real examples from their own experience (a rule the agent got right, something that was caught). Use only what they tell you or what their files show; label it as their experience.
5. Draft a short case (at most one page) in the human's words, with the matching row of the table in the guide, and the honest answers to likely questions. Never add numbers that were not measured, and never call it secure, compliant or production-ready.
6. Do not include file contents, rule titles, names or client details unless the human explicitly chooses to. Do not send it anywhere; the human decides who sees it.

---
name: catch-up
description: Tell the human what changed in this Living System workspace while they were away (new, replaced or retired rules, reviewed and new proposals, handover, repeated work, changed files). Use when the human says they are back from a holiday, sick leave or a break, or asks "what changed since ...".
---

Follow `AGENTS.md` section 9.

1. If the human has not said which day they left, ask once. "About two weeks" is fine: use `--days 14`.
2. Find the Living System folder: `product_folder` in `.living/local.json`. If it is missing, ask the human.
3. Run `python3 <product folder>/tools/living.py since . --date YYYY-MM-DD` (or `--days N`; on Windows: `py` instead of `python3`). It changes nothing.
4. Start with changed rules. For each, say in one line what it means for the human's work now, and offer to read the decision file together. Then proposals, then the rest.
5. At most three items at a time; ask whether they want more. Say why something changed only if a file says so; never guess.
6. End with one next step, usually: run `status` for what waits for them.

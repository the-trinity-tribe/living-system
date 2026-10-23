---
name: practice
description: Let the human practise their own rules and judgement with short situation questions built from their current decisions, so they can work well without AI. Use when the human says "quiz me", "let me practise", "test me on our rules" or "coach me".
---

Follow `AGENTS.md` section 13. Keep it short and friendly; this is practice, not an exam.

1. List the current decisions: `python3 tools/review.py current` (on Windows: `py`). Pick up to three: ones the human uses often, or that changed recently.
2. For each, ask one realistic situation question in plain words, one at a time, without showing the rule first. Example: "A client asks for the report on Sunday and the person who signs it off is away. What happens?"
3. After each answer, open the decision file. Say first what the human got right. Then quote the rule line that matters and name the file.
4. If the rule does not cover the situation, say it is not written down (`AGENTS.md` section 4). Offer to draft a proposal; do not write one unasked.
5. Optionally end with one thinking question: "What would make this rule wrong?" or "What would you check before trusting an AI's answer here?"
6. Keep no score and write nothing, unless the human asks you to note progress in `me/`.

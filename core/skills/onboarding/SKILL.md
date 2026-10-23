---
name: onboarding
description: Introduce a person, step by step, to the rules, role knowledge, workflows and lessons that matter for their work in this Living System workspace (and the linked company workspace). Use when someone is new to a role or company, asks "what should I know?", "what's next on my onboarding?", or starts a session with items still on their path.
---

Follow `AGENTS.md` section 13. Gradual, calm, and never a test.

1. Run `python3 <product folder>/tools/living.py onboard .` (on Windows: `py`). It updates `me/onboarding.md` and shows the next items.
2. Ask whether the human has a few minutes now. If not, say how many items are left and stop.
3. Take one item at a time, at most three per session. Open the file it names and explain it in two or three plain sentences: what it says, and what it means for their daily work. For a rule, give one short example situation.
4. Ask whether it is clear, or offer one quick practice question (the `practice` skill). Answer their questions from the file; say when something is not written down.
5. Only when the human says they understood it, tick it: `living.py onboard . --done <id>`.
6. End with how many items are left. Never rush, grade or keep notes about how well they did.

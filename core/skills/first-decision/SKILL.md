---
name: first-decision
description: Help the human turn one rule from their setup answers or their own words into their first approved decision, through a proposal they approve themselves. Use right after setup, or when the human says "help me make my first decision".
---

Follow `AGENTS.md` section 6e. In short:

1. Take the clearest rule the human stated (usually in `SYSTEM.md`), in their own words and in its narrowest reading. If there is none, ask for one sentence.
2. Show it with `python3 <product folder>/tools/living.py propose . --kind new --title "..." --rule "..." --evidence "setup answer, <date>"` without `--apply`. The product folder is `product_folder` in `.living/local.json`.
3. Say: "This is a proposal, not a rule yet. You decide." Change the wording if asked.
4. After a yes to the wording, run the same command with `--apply`, and show the review command it prints.
5. The human runs it, or names the proposal and says "approve" (then you run it with the name they give).
6. Run `python3 tools/review.py current` and tell them this is now their first rule.

---
name: share-knowledge
description: Hand one piece of role knowledge from this personal Living System workspace to the linked company workspace, without personal information, so the next person in the role does not start from zero. Use when the human says "share this with the team", "hand this on", or agrees to a sharing suggestion.
---

Follow `AGENTS.md` section 14. Nothing reaches the company workspace without the human's yes.

1. Check the link: `.living/local.json` must have `org_folder`, and `.living/profile.json` a `role`. If not, explain `living.py link . --org <folder> --role <role>` and stop.
2. Only files in `knowledge/`, `workflows/` or `lessons/active.md` can be shared. If the knowledge sits somewhere else, offer to write a clean copy in `knowledge/` first, in role terms ("the client", "the team lead"), without names.
3. Show the plan: `python3 <product folder>/tools/living.py share . <file>` (no `--apply`). If it refuses because of contact details, a secret or text addressed to an AI, help the human remove them, then show the plan again.
4. Read the preview with the human. Point out anything that could identify a person or a client, even if the tool did not catch it; it cannot recognise names.
5. After a clear yes, run the same command with `--apply`. Tell the human that someone in the company accepts or rejects it, and that it is not a rule.

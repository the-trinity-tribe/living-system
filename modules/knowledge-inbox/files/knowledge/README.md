# Knowledge

Reusable reference knowledge: facts, sources, how-tos and findings you want to rely on again. Not rules: a knowledge file never overrides a decision, `SYSTEM.md` or `PRINCIPLES.md`.

## How something gets in

1. **Suggest.** The agent may add a suggestion to `inbox.md` (and only there) when it finds something worth keeping, for example a source the human shared or a finding from research. It must name the source and tell the human it added it. It never writes knowledge files directly.
2. **Review.** The human reads the inbox and decides for each item: keep, change or delete.
3. **Keep.** For a kept item, copy `_template.md` to `knowledge/<topic>.md`, fill it in, and set `last_verified` to the date the human checked it. The agent may do the copying when the human names the item and says to keep it. Then delete the item from the inbox.

## Keeping it true

Every knowledge file has a `last_verified: YYYY-MM-DD` line at the top. `doctor` warns when a file was last verified more than 90 days ago, so old facts get a fresh look. After checking a file again, the human (or the agent, when the human says it is still true) updates the date. Never change the date without a human check.

If a knowledge file would change a rule, the agent writes a proposal instead (see `AGENTS.md` section 6).

## Inbox format

```text
---knowledge---
Date: YYYY-MM-DD
Topic: <a few words>
What: <one to three sentences>
Source: <link, document or person, as given; attribution not verified>
---end---
```

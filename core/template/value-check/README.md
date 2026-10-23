# Value check

A small test of whether this system actually helps you. You run it, not the agent.

1. **Before** you rely on the system: write 5 questions about your own work whose real answers you already know (for example "Who has to approve X?"). Put them in `questions.md`.
2. Ask a fresh AI session each question. Do not help it.
3. For each answer, write one word in the **Before** column: `right`, `wrong`, `made up` (it sounded sure but invented it) or `don't know` (it admitted it had no answer).
4. After a few weeks of using the system, ask the same questions in a fresh session and fill the **After** column.
5. Count the results: `python3 <Living System folder>/tools/living.py value-score .` (run it inside this workspace; the scorer lives in the Living System folder you installed from). Or ask your agent to do it.

Write what you noticed in `log.md`. A "made up" answer is the most important thing to watch: it is exactly what this system tries to prevent.

This is your own informal check, not a scientific measurement.

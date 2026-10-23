# Lessons

How your agent learns from mistakes without changing your rules.

- **`inbox.md`**: the agent may add a suggested lesson here (and only here) when you correct it, when a step fails the same way twice, or when you repeat an explanation. It tells you when it does.
- **`active.md`**: lessons you approved. The agent reads them before substantive work. **Only you move a lesson here.**
- The active list holds **at most 20 lessons**. To add one more, merge or retire an old one. Short lists get read; long ones get ignored.

Lessons are working guidance. They are not decisions and can never override a current decision, `SYSTEM.md` or `PRINCIPLES.md`. If a lesson would change a rule, the agent writes a proposal instead (see `AGENTS.md` section 6).

## Inbox format

```text
---lesson---
Date: YYYY-MM-DD
What happened: <one or two sentences>
Lesson: <one sentence the agent should follow next time>
Evidence: <correction by the owner | repeated failure | repeated explanation>
---end---
```

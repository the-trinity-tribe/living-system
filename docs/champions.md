# Making the case: a guide for people who tried it

Status: EXPERIMENTAL. Version: 0.2.0.

You used Living System at work and want your CEO, CTO or founder to consider it. This page helps you argue from what you saw, not from promises. Every argument here is something you can check or show.

## 1. Bring evidence, not adjectives

Make a summary of your own workspace. It contains counts only, never content, names or titles:

```sh
python3 tools/living.py evidence ~/my-workspace --out ~/Documents/living-system-evidence.md
```

Read it before you share it. It reports four kinds of value separately (human experience and agency, business outcomes, reliability, resources) and says what was not measured. Then add, in your own words and clearly labelled as yours:

- **One example** of a time the agent gave the right answer because a rule was written down (from your value check log).
- **One example** of something that was stopped or caught: a proposal instead of a quiet rule change, a refused self-approval, a guard block, a changed decision found by `verify`.
- **Your value check table** (before/after). It is in the summary if you did the test.

Do not add numbers you did not measure. If you want to talk about time saved, time one task for two weeks before and after, and say that it is one person's measurement.

## 2. What each person usually cares about

| Who | Their question | What you can honestly show |
| --- | --- | --- |
| **CEO** | Does it keep knowledge when people leave or change roles? Does it reduce mistakes from outdated rules? | Role knowledge handed on and accepted (count in the summary); `since` and the onboarding path after a rule changed; the review record showing that approved rules were not changed afterwards. |
| **CTO** | What does it run on, what does it touch, can we get out? | Plain Markdown and JSON files; Python standard library only; works with Claude Code and Codex from the same files; no server, no account, no network calls by its tools; `export` makes one zip. Automatic tests run on Linux, Windows and macOS. Limits are written down (below). |
| **Founder** | Cost, speed, control. | No licence fee (MPL-2.0). A workspace takes minutes to set up. Humans approve every rule; agents can only propose. A pilot needs two people and two weeks. |
| **Team lead** | Will my people use it? Who approves what? | Profiles for employees and managers; in a team workspace whoever proposes a change cannot approve it; the agent explains its choices and can coach people so their skills stay sharp. |

## 3. Questions you will get, and honest answers

- **"Is it secure?"** It is not a security product. There is no login, no access control and no identity check; names in approvals are labels. It keeps secrets out of the workspace where the agent writes, scans outside material for hidden instructions, and records reviews so later changes show up. Access is whatever your folders, git and drives allow.
- **"Is it compliant (GDPR, ISO, …)?"** It makes no compliance claim. It can support your process by keeping rules, approvals and their history in plain files you control. Personal data rules still apply to what people write in it.
- **"Why not just a wiki or a shared drive?"** The difference is the agent rules: the AI answers from approved rules, names the file, says when something is not written down, and cannot change a rule on its own. A wiki is still useful; Living System can sit next to it.
- **"What if the AI vendor changes?"** The same files work with two agents today, and `handbook` prints the rules and steps for working with no AI at all.
- **"Who maintains it?"** Be honest: it is an experimental open-source project. Version 0.2.0. Check the changelog and the tests yourself.

## 4. A small pilot to suggest

Two weeks, two to five people, one team:

1. A manager creates the company workspace (`init --team`) and writes three real rules as proposals; someone else approves them.
2. Each person creates a personal workspace and links it (`link`).
3. Everyone does the value check before and after.
4. At the end: each person runs `evidence`; the team compares notes in a 30-minute meeting. Decide to stop, continue or widen.

## 5. What not to say

- Do not promise savings, accuracy rates or "AI that follows rules". Say what you saw in your own workspace.
- Do not call it secure, compliant, production-ready or enterprise-grade. It is none of these claims.
- Do not share someone else's workspace, or content from yours, to make the case. The evidence summary exists so you do not have to.

# Feature: learning mode (coach, practice and the handbook)

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

It helps you keep your own skills while an AI does more of the work. Four parts:

- **Always on:** the agent says why it chose an approach, shows you the steps when you ask "how did you do that?", and says plainly when it is unsure.
- **Coach mode (you switch it on):** the agent offers to let you try a task first and checks it after, adds "how to do this yourself" steps, and now and then asks one honest question that tests a plan.
- **Perspectives:** for an important decision, say "look at this from different angles": the agent sets out three or four genuinely different viewpoints (named by role, never as real people), keeps evidence apart from interpretation, and leaves the decision to you.
- **Practice and handbook:** the `practice` skill asks you short situation questions about your own rules. `living.py handbook` writes a readable copy of your rules and workflows, so you can work without AI.

## Why would someone need it?

When an AI does a task every time, people stop practising it. If the AI is down, wrong or not allowed, they cannot do the work or tell whether an answer is right. Living System is built so the human stays in charge; that only works if the human can still judge the work.

## What problem does it solve?

- Skills fade without practice: coach mode and practice keep them in use.
- Agreeing too quickly with an AI: one critical question at the right moment.
- "What if the system fails?": the handbook gives you the rules and steps on paper.

## What does it require?

A Living System workspace and Python 3.10 or newer. The coach and practice parts need Claude Code or Codex; the handbook needs only Python.

## How do you install or enable it?

- During setup the agent asks whether you want coaching. Or: `python3 tools/living.py init ~/my-workspace --profile employee --language en --coach`.
- Later: tell your agent "switch coach mode on" (or off). It changes `coach` in `.living/profile.json` after your yes.
- Write the skills you want to keep in `me/goals.md` (the line "Skills I want to keep doing myself, even with AI").

## How do you use it?

- Say "quiz me on our rules" or "let me practise". The agent asks up to three situation questions, one at a time, and checks your answer against the decision file.
- Make the handbook, saved outside the workspace:

```sh
python3 tools/living.py handbook ~/my-workspace --out ~/Documents/handbook.md
```

Without `--out` it is printed on screen.

## Example scenarios

- You want to keep writing client e-mails yourself. In coach mode the agent asks "Do you want to try it first? I will check it after."
- You say "We'll drop the second check for this client". The agent asks once: "What could go wrong without it?", then helps either way.
- Before a holiday you print the handbook for the colleague who covers you.

## What changes inside the system when it runs?

- `init --coach` stores `"coach": true` in `.living/profile.json`. `upgrade` keeps your choice.
- `practice` changes nothing and keeps no score.
- `handbook` reads the workspace and writes only the file you name, outside the workspace. It replaces a file only if it is an earlier handbook.

## Where does the human keep control?

- Coach mode is off unless you switch it on. Every offer can be declined; critical questions are asked once and never block the work.
- No scores, grades or judgements about you are stored. Progress notes go in `me/` only if you write them or say yes.
- The handbook is a copy. The files in `decisions/` stay the rules.

## What can go wrong, and how do you undo it?

- **Coaching is instruction-only.** An agent may forget to offer it. Say "coach me on this" to ask directly.
- **The handbook gets out of date** when a rule changes. Make it again; it says on top when it was made.
- **Too many questions?** Switch coach mode off: "switch coach mode off".

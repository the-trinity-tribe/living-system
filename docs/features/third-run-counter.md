# Feature: Third-Run counter

Status: EXPERIMENTAL. Version: 0.3.0.

## What does this feature do?

It keeps a small, visible count of how often a kind of work comes up, such as a weekly update or notes after a call. At the third time, your agent offers you a choice: automate it with a module or a workflow, improve it (keep doing it by hand, but write down better steps), keep doing it by hand, or decide later. If a task costs you a lot of effort and is safe and easy to undo, the agent may offer to automate it sooner.

## Why would someone need it?

Automating too early wastes time on the wrong thing; never automating means doing the same work by hand forever. The Third-Run Rule says: do it by hand a few times first, so you understand it, then decide.

## What problem does it solve?

- Suggestions are based on a real count, not on the agent's guess or one passing mention.
- You decide once, and the decision is remembered across sessions and agents.
- Nothing is watched in the background: the agent counts only work you ask it to do, and says so each time.

## What does it require?

A Living System workspace. No module is needed; the count works on its own and suggests modules when one fits.

## How do you install or enable it?

Nothing to install. Workspaces record where the Living System folder is (`.living/local.json`, kept out of shared repositories by `.gitignore`), so the agent can count without asking.

## How do you use it?

Work as usual. When you ask for something that usually repeats, the agent counts it and tells you in one line. At the third time it asks you to choose. You can also use the command yourself:

```sh
python3 tools/living.py runs ~/my-workspace                              # what has been counted
python3 tools/living.py runs ~/my-workspace --add weekly-update          # count one more
python3 tools/living.py runs ~/my-workspace --decide weekly-update later --after 2
python3 tools/living.py runs ~/my-workspace --forget weekly-update       # delete the entry
```

Say "don't count this" to your agent, and it stops and deletes the entry.

## Example scenarios

- Three Fridays in a row you ask for a client update. On the third, the agent says it has come up three times and offers the `weekly-update` module, keeping it manual, or later.
- You choose "later". Three runs on, it asks again.
- You do call notes differently every time and want no suggestion. You choose "manual", and the agent stops offering.

## What changes inside the system when it runs?

Only `.living/runs.json` changes. It holds, per kind of work, a short name, a count, the first and last date and your decision. It never holds content or names of people or clients; the tool refuses names that are not short lowercase words with hyphens. `status` lists work that has reached the third run without a decision.

## Where does the human keep control?

- The agent counts only what you ask it to do, and tells you each time.
- The choice at the third run is yours; the agent records it only from your answer.
- You can read the file any time, and delete an entry or the whole file.

## What can go wrong, and how do you undo it?

- **The same work was counted under two names:** when a new name is added, the tool lists the names already counted; remove the duplicate with `--forget` and count it under the existing name.
- **You do not want counting:** tell your agent, or delete `.living/runs.json`.
- **The file is damaged:** `status` says so; delete the file to start again.
- **Limits:** counting is an instruction to the agent, which can forget to count. Counts are per workspace and per computer.

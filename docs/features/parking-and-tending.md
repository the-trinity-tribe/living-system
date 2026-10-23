# Feature: parking ideas, tending, and checking ideas

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

Small helpers that protect your attention:

- **Focus mode:** while it is on, the agent does what you ask and suggests nothing else. `python3 tools/living.py focus ~/my-workspace on` (or `off`), or just say "focus mode on".

- **Park:** an idea that pops up mid-task is written down in one line, and the work carries on.
- **Tend:** when you have a few minutes, the agent walks you through everything that is waiting, one item at a time.
- **Idea check:** before building something, a short set of questions helps you decide whether it is worth it and what the smallest useful version is. It can also end in "don't build it".

## Why would someone need it?

New ideas pull you away from what you are doing, and unfinished items pile up until they feel heavy. Writing an idea down lets you let go of it. A calm, item-by-item pass is easier than facing a long list. And many ideas are not worth building, which is easier to see with a few honest questions.

## What problem does it solve?

- You don't switch tasks every time an idea comes up.
- Waiting items get handled in small steps instead of all at once.
- Less is built that nobody needs.

## What does it require?

A Living System workspace and Python 3.10 or newer. Tend and idea check need Claude Code or Codex.

## How do you install or enable it?

Nothing to install. Say "park this", "let's tend", or "is this idea worth it?". Or run:

```sh
python3 tools/living.py park ~/my-workspace "Ask the team about a shared calendar"
python3 tools/living.py park ~/my-workspace
python3 tools/living.py park ~/my-workspace --done 1
```

## How do you use it?

- **Park:** say it in one line. The agent parks it and goes back to the task.
- **Tend:** say how much time you have. The agent takes one item, explains the choices, does what you choose, and stops when the time is up.
- **Idea check:** answer up to seven short questions. "Don't know" is fine. At the end you choose: build the smallest version, try it by hand first, park it, or drop it.

## Example scenarios

- In the middle of a client update you think of a newsletter. "Park this: a newsletter for clients." The update continues.
- On Friday afternoon: "Let's tend for ten minutes." The agent shows a waiting proposal, then a knowledge file due for a re-check, then your parked newsletter idea, and offers the idea check for it.
- The idea check shows that the newsletter would take two hours a week and only three clients asked. You choose "try it by hand first".

## What changes inside the system when it runs?

- `park` adds one dated line to `me/parked.md`, or ticks one off. Listing changes nothing. `status` shows how many ideas are parked.
- Tend runs the same commands you could run yourself (`status`, `runs --decide`, `park --done`), and only after your choice.
- Idea check writes nothing unless you choose to park the idea.

## Where does the human keep control?

- Parked ideas are private (in `me/`) and not rules.
- In tend, every item is your decision. Proposals are still approved only when you name them and say "approve".
- The idea check gives choices, not a verdict, and never invents numbers for time or money saved.

## What can go wrong, and how do you undo it?

- **Too many parked ideas?** Tend through them, or tick off the ones you no longer care about.
- **Parked something private?** Edit or delete the line in `me/parked.md`. Passwords and keys are refused.
- **The agent starts on a parked idea anyway?** Say "it's parked, back to the task". The rule in `AGENTS.md` says it should not.

# Feature: personal work agreement

Status: EXPERIMENTAL. Version: 0.3.0.

## What does this feature do?

Every workspace has a short file, `me/agreement.md`, where you write down how you want to work with AI: how you like answers, what you do yourself and what the agent may do, when not to interrupt you, the skills you want to keep, what must never be handed over, what may be shared, when you want explanations, when you want to be challenged, and what time saved by the agent is for. Your agent reads it at the start of every session and follows it.

## Why would someone need it?

People work differently, and an agent cannot know your boundaries unless you tell it. Saying them once, in your own words, is easier than repeating them in every session. And writing them down keeps them yours: nothing is guessed or recorded about you behind your back.

## What problem does it solve?

- Your preferences survive new sessions, new agents and new computers.
- Interruptions, explanations and challenges happen on your terms.
- Time the agent saves you is not quietly turned into more work.

## What does it require?

A Living System workspace. The agent part needs Claude Code or Codex.

## How do you install or enable it?

New workspaces have it, in English, German or Polish. Older workspaces get it with `living.py upgrade` (it is only added if you have none; nothing in `me/` is ever changed by an upgrade).

## How do you use it?

Open `me/agreement.md` in any editor and write a line or two under the headings that matter to you; leave the rest. Or tell your agent "help me fill in my work agreement"; it asks and writes only what you say. Change it any time.

## Example scenarios

- "When to challenge me: ask one honest question when a plan affects clients." The agent does that, once, and then helps either way.
- "When not to interrupt me: no suggestions while I write." Ideas go to your parked list instead.
- "What time saved is for: learning and a proper lunch break." The agent does not suggest more tasks to fill it.

## What changes inside the system when it runs?

Nothing runs. It is a plain file the agent reads. `living.py agency` shows whether you have one.

## Where does the human keep control?

- You write it; the agent never adds to it on its own or guesses things about you.
- An instruction you give in the moment comes first. The agreement never changes the rules in your decisions, `SYSTEM.md` or `PRINCIPLES.md`.
- For employees, `me/` is left out of shared repositories by default. For other profiles, keep that in mind before you share the workspace.

## What can go wrong, and how do you undo it?

- **It is an instruction, not a lock.** An agent can miss it; remind it, and use [focus mode](parking-and-tending.md) (`living.py focus`) and the `coach` and `calm_replies` settings in `.living/profile.json` for the parts that have a switch.
- **It gets long.** Keep it to what you actually want followed; shorter is read more reliably.
- **Want it gone?** Delete the file. Nothing else depends on it.

# Feature: catch-up ("what changed while I was away")

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

After a holiday, sick leave or a long break, it tells you what changed in your workspace since the day you left. Changed rules come first. It changes nothing.

## Why would someone need it?

Coming back is the moment you are most likely to follow an old rule. Someone approved a new one, replaced one, or a proposal waits for you, and nobody told you. Catch-up gives you the short list, in the right order, instead of a pile of files.

## What problem does it solve?

- You do not work from a rule that was replaced while you were away.
- You see which proposals were approved, rejected or are new.
- You see where the work stopped and what other files changed, without reading everything.

## What does it require?

A Living System workspace and Python 3.10 or newer.

## How do you install or enable it?

Nothing to install. Tell your agent "I'm back from two weeks of holiday, what changed?". The `catch-up` skill and `AGENTS.md` section 9 tell it what to do. Or run it yourself from the Living System folder:

```sh
python3 tools/living.py since ~/my-workspace --date 2026-10-01
python3 tools/living.py since ~/my-workspace --days 14
```

## How do you use it?

Give the day you left (or how many days you were away). Read the rules section first; then run `status` for what waits for you. The agent gives at most three items at a time and asks whether you want more.

## Example scenarios

- You were away two weeks. While you were gone, the rule "Reports go out on Fridays" was replaced by "Reports go out on Mondays". Catch-up lists it first: "Replaced: Reports go out on Fridays. Now read decisions/...".
- A colleague's proposal was rejected and a new one waits for review. Both appear under "Proposals".
- Someone counted the weekly update a third time. Catch-up says it now waits for your decision.

## What changes inside the system when it runs?

Nothing. It only reads:

- **Rules:** the `date` of each approved decision in `decisions/`, and whether it is new, replaces, amends or retires an older one. Also whether `SYSTEM.md` or `PRINCIPLES.md` was edited.
- **Proposals:** their `date` and `reviewed_on`.
- **Repeated work:** the last date in `.living/runs.json`.
- **Everything else:** file dates on this computer. Files still exactly as Living System installed them are left out.

## Where does the human keep control?

Catch-up only reports. It cannot approve, change or undo anything. It says what the files show; why something changed is in the files themselves (the proposal's "Why" section), and the agent must not guess.

## What can go wrong, and how do you undo it?

- **File dates can mislead.** Copying a workspace, restoring an export or a `git pull` can give files a new date. Treat "Other files changed" as a hint; the rules and proposals sections come from dates written inside the files.
- **A date typed by hand in a decision or proposal** is what catch-up trusts. If someone wrote a wrong date, the item may appear in the wrong place. `python3 tools/review.py history` shows the full list.
- There is nothing to undo: it writes nothing.

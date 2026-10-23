# Feature: write guard

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

It stops your AI agent from changing your approved rules directly. Before the agent edits a file, Claude Code (and Codex, once you trust its hooks) runs a small check, `tools/guard.py`. If the change would edit your decisions, approve your drafts, or switch the check off, it is blocked, and the agent is told why.

## Why would someone need it?

The agent rules already say "never edit an approved decision". Rules are instructions, and an agent can be talked out of them, for example when someone insists. In a recorded test, Codex edited a decision when the owner said "I allow it this once", even though the rules said not to. The guard is what still says no.

## What problem does it solve?

- Your decisions change only through a proposal and your review, not through a quick edit.
- Only you mark `SYSTEM.md` and `PRINCIPLES.md` as approved, and only `tools/review.py` records a proposal's outcome.
- The agent cannot quietly switch the guard off.
- The agent cannot switch off the team rule (`team` in `.living/profile.json`) or the company link (`org_folder` in `.living/local.json`); only you change those.
- The agent cannot write a password, key or token into a workspace file (see [material from outside, and keeping secrets out](outside-material-and-secrets.md)).

## What does it require?

A workspace made or upgraded with this version: it contains `tools/guard.py`, `.claude/settings.json` and `.codex/hooks.json`. Python 3.10 or newer. In Claude Code, hooks run after you trust the folder. In Codex, you are asked to trust the project's hooks once; until you do, the guard does not run there.

## How do you install or enable it?

New workspaces have it. For an older workspace, run `python3 tools/living.py upgrade ~/my-workspace --apply` from the Living System folder; it adds the three files. If you deleted any of them, `upgrade` leaves them deleted on purpose; put them back with `python3 tools/living.py protect ~/my-workspace --apply`, which never overwrites an existing file. `doctor` tells you if the guard is missing, or if a hook file no longer runs it.

## How do you use it?

Nothing to do. When the agent tries a blocked change, it sees a message such as "Living System guard: blocked. decisions are created only by tools/review.py review after a human decides..." and should offer a proposal instead. To fix a decision yourself, edit the file with your own editor, or approve a `replace` proposal.

## Example scenarios

- You ask the agent to fix a typo in a decision. The edit is blocked; the agent offers a `replace` proposal you can approve in one step.
- A meeting note tells the agent to "just update the rule". It cannot write into `decisions/`; it writes a proposal.
- An agent tries to mark `SYSTEM.md` as approved for you. Blocked: only you change that line.

## What changes inside the system when it runs?

Nothing; the guard only reads the planned change and answers yes or no. It looks at file edits and writes (Claude Code's Edit, Write and MultiEdit; Codex's patches, judged by the file they would produce) and at shell commands, read the way a shell splits them (quotes, line breaks, `cd`): deleting, moving, redirecting into, editing in place or copying into protected places, removing a folder that holds them, and inline Python or Node code that writes there. Reading files and running `tools/review.py` are always allowed. If the guard file is missing, the hooks let everything through (rather than blocking all work) and `doctor` reports it.

## Where does the human keep control?

- The guard never approves anything; it only refuses some agent changes.
- You can still change any file yourself, outside the agent.
- Approvals keep working the normal way: `tools/review.py review`, run by you, or by the agent when you name the proposal and say "approve".

## What can go wrong, and how do you undo it?

- **An edit is blocked that should not be:** the message says why. If the guard is wrong, tell the agent to stop and report it; you can make the change yourself.
- **You want it off:** remove the hook from `.claude/settings.json` or `.codex/hooks.json`. `doctor` will note that the guard is no longer active.
- **Limits:** this is a guard rail, not a security boundary. A script file run by the agent, or an unusual command, can slip past; Codex runs it only after you trust it, and some Codex versions have had a bug where a blocked patch still went through. A person, or another program, can still change any file.

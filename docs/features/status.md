# Feature: status

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

It tells you, in a few plain lines, what needs your attention in your workspace. It changes nothing.

## Why would someone need it?

After a few days away it is hard to remember what is waiting for you. Status gives you the short list, so you can start with the right thing instead of reading every file.

## What problem does it solve?

- Proposals do not sit unreviewed because you forgot them.
- Drafts you never approved are easy to spot.
- You see where the last session stopped, with any agent.

## What does it require?

A Living System workspace and Python 3.10 or newer.

## How do you install or enable it?

Nothing to install. Run it from the Living System folder:

```sh
python3 tools/living.py status ~/my-workspace
```

Or ask your agent "What needs my attention?". The workspace rules tell it to run `status` and explain the result.

## How do you use it?

Run it at the start of a work session. Deal with the items under "Waiting for you", then run it again.

## Example scenarios

- A meeting-notes run staged two proposals. Status lists both, with their kind and title, so you know what to review.
- You installed `staged-learning`, and the agent suggested a lesson. Status says one lesson waits in `lessons/inbox.md`.
- You are new. Status reminds you that `SYSTEM.md` and `PRINCIPLES.md` are still drafts.

## What changes inside the system when it runs?

Nothing. Status only reads files:

| Line | Where it comes from |
| --- | --- |
| Rules in force | the number of current decisions, the same list as `review.py current` |
| Proposals to review | files in `proposals/` whose status is `proposed` or `deferred`, each with the exact review command to copy once you have decided |
| Lesson suggestions | `---lesson---` blocks in `lessons/inbox.md`, if that module is installed |
| Knowledge suggestions and re-checks | `---knowledge---` blocks in `knowledge/inbox.md`, and knowledge files last verified more than 90 days ago |
| Drafts | `SYSTEM.md` and `PRINCIPLES.md` without `status: approved` |
| Last session's next step | the "next step" line in `handover/LATEST.md` |
| Health | the error and warning count from `doctor` |

## Where does the human keep control?

Status never approves, installs or edits anything. It only points at what you may want to do.

## What can go wrong, and how do you undo it?

- **A proposal is listed as unreadable:** its front matter is broken. Run `doctor` and fix the file it names.
- **The next step is missing:** the handover note has no "next step" line yet. Ask your agent to write the handover note at the end of a session.
- **Limits:** status counts only what is written in files. It does not know about work that happened outside the workspace.

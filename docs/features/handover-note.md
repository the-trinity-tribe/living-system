# Feature: handover note

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

The note holds the date, the goal in one line, what was done, what is open (with one open question if there is one), proposals waiting, and one next step. `status` points out when the note is older than later changes in the workspace.

It is one file, `handover/LATEST.md`, where your agent writes down where the last work session stopped. The next session reads it and can continue.

## Why would someone need it?

Each AI session starts empty. Without a note, you explain again what was done, what is open, and what comes next.

## What problem does it solve?

It reduces lost context between sessions. The note points to files in your workspace instead of repeating them.

## What does it require?

A workspace and an agent that follows `AGENTS.md` (Claude Code or Codex). There is no tool for this feature. It is an instruction to the agent, written in `AGENTS.md` section 9.

## How do you install or enable it?

Nothing to install. Every workspace has `handover/LATEST.md`. At the start it says "No session has been handed over yet."

## How do you use it?

At the end of a session, or whenever you ask ("write the handover note"), the agent replaces the text in `handover/LATEST.md` with:

- **Date and what we worked on.**
- **What was done** (pointing to files).
- **What is still open.**
- **Proposals waiting for your review** (file names).
- **One next step for you.**

In the next session, `CONTEXT-ROUTING.md` sends the agent to this file when it needs to know where the last session stopped.

The `employee` profile also adds `handover/team-handover-template.md`. It is for handing work to a colleague. Share only what your employer allows.

## Example scenarios

- You stop on Friday with a proposal waiting. On Monday you open a fresh session and the note names the proposal file and one next step.
- You hand a project to a colleague. You copy the team template and fill it in. You point to approved decisions, and write "not written down" where nothing is.

## What changes inside the system when it runs?

One file changes: `handover/LATEST.md`. The agent may write it without being asked. Without being asked, it may create only a proposal, this note and, if an installed module allows it, one more file named by that module (`AGENTS.md` section 4).

**The note is not canonical.** It never outranks `SYSTEM.md`, `PRINCIPLES.md`, current decisions or your instructions. Facts in it point to files. They are not new rules. A rule written only in the note is not a rule.

## Where does the human keep control?

- The note cannot change a rule. Rules change only through [proposals and review](decisions-and-proposals.md).
- You can edit or delete it. It is a plain file.
- You read it before the next session if you want to.

## What can go wrong, and how do you undo it?

- **The agent forgets to write it.** Nothing forces it. No command creates, checks or reads the note, and neither `review.py check` nor `doctor` looks at it. Ask for it at the end of each session.
- **The note is wrong or stale.** The agent may trust it too much. Because it is not canonical, a current decision wins when they disagree. Fix or delete the note.
- **Sensitive details.** The note is part of your workspace. Keep secrets out of it.
- **Undo:** replace the text with the original sentence "No session has been handed over yet." or restore it from Git.

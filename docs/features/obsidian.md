# Feature: reading your workspace in Obsidian (or any editor)

Status: EXPERIMENTAL. Version: 0.3.0.

## What does this feature do?

It explains how to read and work with your workspace in a note-taking app such as Obsidian, instead of a terminal or code editor. Living System is plain Markdown files, so Obsidian can open the workspace folder as a "vault" without any conversion.

## Why would someone need it?

Most people do not want to read rules and project notes in a terminal. A note app shows them as readable pages with search, and lets you change a draft's status with a click.

## What problem does it solve?

- Reading your rules, projects and handover notes is comfortable and quick.
- Approving `SYSTEM.md` or `PRINCIPLES.md` is a visible, deliberate change of one field.
- You stay independent: Obsidian is optional, and any Markdown editor works the same way.

## What does it require?

A Living System workspace and Obsidian (free for personal use, from obsidian.md) or another Markdown editor. Nothing in Living System depends on it.

## How do you install or enable it?

In Obsidian, choose **Open folder as vault** and pick your workspace folder. That is all. Obsidian adds its own settings folder, `.obsidian/`, which belongs to you; the workspace `.gitignore` already keeps Obsidian's window layout files out of shared repositories.

## How do you use it?

- **Read:** start with `README.md`, then `SYSTEM.md`, `decisions/` and `handover/LATEST.md`. Use search to find any rule.
- **Approve your drafts:** open `SYSTEM.md` (and `PRINCIPLES.md`). The `status` field appears as a property at the top. When the text is right, change `draft` to `approved`. Only you do this; the agent is blocked from it.
- **Write:** projects, knowledge and your own notes in `me/` are yours to edit.
- **Decisions:** do not edit files in `decisions/`, even though Obsidian would let you. Ask your agent for a proposal (`propose-change`) and approve it with the review command. That keeps the history honest.
- **Review proposals:** read them in Obsidian, then run the review command shown by `status` in a terminal, or tell your agent "approve proposals/<file>".

## Example scenarios

- On Monday morning you open the vault, read `handover/LATEST.md` to see where you stopped, and check `proposals/` for anything waiting.
- After setup you read the draft `SYSTEM.md` in Obsidian, fix one sentence, and switch its status to `approved`.
- A colleague asks who approves invoices. You search the vault for "invoice" and find the decision.

## What changes inside the system when it runs?

Nothing in Living System changes. Obsidian adds `.obsidian/` to the folder. `doctor`, `status` and `upgrade` ignore it, and `export` includes it, because it is your setting.

## Where does the human keep control?

- Everything you change in Obsidian is your own change; the write guard only stops agents.
- Approving drafts and reviewing proposals stay explicit steps.

## What can go wrong, and how do you undo it?

- **A decision file was edited by hand:** run `python3 tools/review.py history` and `doctor`; restore the old text from a backup or git, and make the change through a `replace` proposal instead.
- **Sync and publish:** Obsidian's optional Sync and Publish services, and any cloud folder, put your files on someone else's servers. Check their terms before you sync private or client information; do not publish a workspace.
- **Links:** paths in the files are written as `code`, not as links, so they are not clickable in Obsidian. Use search or the file list.
- **Limits:** this guide is not tested against every Obsidian plugin. Plugins that rewrite files (formatters, linters) can change files the tools expect in a fixed shape; switch them off for `decisions/` and `proposals/`.

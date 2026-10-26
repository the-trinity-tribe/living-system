# Feature: atlas

Status: EXPERIMENTAL. Version: 0.3.0.

## What does this feature do?

`living.py atlas` draws a map of your workspace: which rules are in force, which projects, workflows and knowledge files rely on each rule, how rules replaced each other over time, and which files still point to a rule that is no longer in force. It also counts workflows, knowledge (in use and archived) and lessons. The map includes a diagram that GitHub, Obsidian and many Markdown editors draw for you.

## Why would someone need it?

After a few months, a workspace has many rules and files. Before changing a rule, you want to know what depends on it; after a change, you want to know what still points to the old version.

## What problem does it solve?

- You see what a rule change would affect.
- Files that still rely on an old rule are easy to find.
- New people get an overview in one page.

## What does it require?

A Living System workspace and Python 3.10 or newer.

## How do you install or enable it?

Nothing to install.

```sh
python3 tools/living.py atlas ~/my-workspace
python3 tools/living.py atlas ~/my-workspace --out ~/Documents/atlas.md
```

## How do you use it?

Run it before changing a rule, after a catch-up, or when someone new joins. Open the saved file in an editor that shows Mermaid diagrams to see the picture; the lists below it are complete either way.

## Example scenarios

- Before replacing the rule on report days, the atlas shows that the weekly-update workflow and two projects rely on it.
- After the replacement, it lists one workflow that still names the old rule; you update it.

## What changes inside the system when it runs?

Nothing. It reads the files. With `--out` it writes one file outside the workspace.

## Where does the human keep control?

The atlas is a view, not a source: your Markdown files stay the truth. It never edits a reference for you.

## What can go wrong, and how do you undo it?

- **It only sees written references.** A file that relies on a rule without naming its file (for example `decisions/2026-10-21-mondays.md`) does not appear as a link.
- **Big workspaces.** The diagram shows the first 40 links; the lists show everything.

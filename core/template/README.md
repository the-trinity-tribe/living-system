# My Living System workspace

This is your own workspace. It was created by `tools/living.py init`. It is plain Markdown files on your computer. Nothing is uploaded anywhere by this system.

**The idea:** you decide what is true. Your AI agent reads these files, helps with your work, and *proposes* changes. It never changes your rules by itself.

## First steps

1. Open this folder in Claude Code or Codex. The agent reads `AGENTS.md` first.
2. Read `SYSTEM.md` and `PRINCIPLES.md`. They are **drafts**. When you are happy with one, change `status: draft` to `status: approved` yourself.
3. Run the value check (`value-check/README.md`) before you rely on it.
4. Check the structure any time: `python3 tools/review.py check` (prints `ok` when fine). To see what is waiting for you, run `python3 <Living System folder>/tools/living.py status .`. For a fuller check in plain words, run `python3 <Living System folder>/tools/living.py doctor .`

**Reading the files:** any Markdown editor works. Obsidian can open this folder as a vault: the `status` line appears as a property you can change when you approve a draft. Do not edit files in `decisions/` by hand; change rules through a proposal. See the Obsidian guide in the Living System docs (`docs/features/obsidian.md`).

## What is in here

| Folder or file | What it is |
| --- | --- |
| `AGENTS.md` | Rules for the agent. |
| `SYSTEM.md`, `PRINCIPLES.md` | Who you are and what you stand on. Draft until you approve. |
| `decisions/` | Your approved rules. One file per rule. Never edited, only replaced. |
| `proposals/` | Changes the agent suggests. Not rules until you approve them. |
| `projects/`, `knowledge/`, `workflows/` | Your working context. |
| `handover/LATEST.md` | Where the last session stopped. |
| `value-check/` | Your own test of whether this helps. |
| `.living/` | Setup choices and a list of the original files. |

## Language

Your content can be in any language. A few words must stay **English** because the tools read them: the front matter keys (`status`, `target`, `kind`, ...) and the headings `## Rule`, `## Why`, `## Scope`, `## Proposed future state`, `## Why and open questions`, `# Proposal:`. The text under them is in your language.

These starter files are in English. With `--language de` or `--language pl` they come in German or Polish instead. The rules for the agent (`AGENTS.md`, `CLAUDE.md`) stay English in every language, so there is one tested rule set. Your agent still replies and writes new content in the language you chose.

## Updating

When a newer Living System comes out, run `python3 <Living System folder>/tools/living.py upgrade .` here to see what would change, then add `--apply`. It updates only files you never changed. For files you edited, it keeps yours and saves the new version in `.living/upgrade/`. It never touches `decisions/`, `proposals/`, `projects/` or `me/`.

## Undo

Delete this folder. Nothing else was changed on your computer.

## Limits

Experimental. It does not verify who you are, does not protect files from being read, and an agent can still ignore instructions. Do not treat it as a security tool.

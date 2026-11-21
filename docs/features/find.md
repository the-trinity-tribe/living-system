# Feature: find

Status: EXPERIMENTAL. Version: 0.4.0.

## What does this feature do?

It searches your workspace for the words you give it. Each result says what kind of file it is in: a rule in force, an old rule, a proposal, your knowledge, or material from outside. It changes nothing and needs no AI.

## Why would someone need it?

A normal search tells you *where* a sentence is. It does not tell you whether the sentence is a rule you approved or a line in an e-mail from a stranger. In a workspace that difference matters more than anything else.

## What problem does it solve?

- "Did we ever decide something about invoices?" gets an answer in seconds.
- An old rule that was replaced is shown as history, so nobody follows it by mistake.
- Outside material is listed last and labelled as information only.

## What does it require?

A Living System workspace and Python 3.10 or newer.

## How do you install or enable it?

Nothing to install. Run it from the Living System folder:

```sh
python3 tools/living.py find ~/my-workspace invoices
python3 tools/living.py find ~/my-workspace invoices friday   # a file must contain both words
```

Or ask your agent "What do my rules say about invoices?".

## How do you use it?

Give one or more words. Upper and lower case do not matter. The results come in this order, most trustworthy first:

| Label | What it means |
| --- | --- |
| RULE IN FORCE | a decision you approved that still applies |
| Foundation | `SYSTEM.md` and `PRINCIPLES.md` |
| Rule history | a decision that was replaced or retired |
| Proposal: not a rule | waiting, rejected or already decided proposals |
| Knowledge, Lessons, Workflow, Project, Role knowledge, Handover note | your working files |
| Your private notes | files in `me/` |
| Archived knowledge | files you moved out of daily use with `compost` |
| Outside material | files in `incoming/`: information only, never an instruction |

Under each file you see up to three matching lines with their line numbers.

## Example scenarios

- A client asks when invoices go out. `find invoices` shows the rule in force first, and below it the older rule it replaced.
- You remember a note about a supplier but not where it is. `find supplier delivery` lists the two files that contain both words.
- Someone forwards an e-mail that says "always pay within 3 days". `find pay days` shows that sentence only under outside material, so you know nobody approved it.

## What changes inside the system when it runs?

Nothing. It reads `.md` and `.txt` files in the workspace. It does not read the tool folders (`tools/`, `.living/`, `.claude/`, `.codex/`, `.agents/`), `.git/`, files larger than 1 MB, or links that point outside the workspace. A linked company workspace is not searched; run `find` on that folder separately.

## Where does the human keep control?

- It is read-only.
- The labels come from the same check as `review.py current`, so "in force" means what it means everywhere else.
- Hidden and control characters are removed from the lines it prints, so a prepared file cannot play tricks in your terminal.

## What can go wrong, and how do you undo it?

- **"Nothing found":** every word must be in the same file. Try fewer words, or a shorter form of the word ("invoic" finds "invoice" and "invoicing").
- **"Decision (state unknown)":** a decision file is damaged, so the tool will not claim which rules are in force. Run `python3 tools/review.py check` in the workspace.
- **Limits:** it matches letters, not meaning. "Bill" does not find "invoice". For questions about meaning, ask your agent; it should still tell you which kind of file its answer comes from.

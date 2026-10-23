# Manual test checklist

A step-by-step check of a Living System release on a real computer. It takes about 45 minutes. Written for Windows (PowerShell); on macOS or Linux type `python3` instead of `py` and `/` instead of `\`.

Work through it in order. For each step, compare what you see with **Expect**. If it does not match, copy the exact text from the window (not a summary) into the results table at the end, and carry on.

Use a throwaway workspace folder (`~\ls-test` below). Delete it when you are done.

## 0. Before you start

| Step | Command | Expect |
| --- | --- | --- |
| 0.1 | `py --version` | `Python 3.10` or newer. If `py` is not found: install Python from python.org and tick "Add python.exe to PATH". |
| 0.2 | `git --version` | A version number. |
| 0.3 | `git clone https://github.com/the-trinity-tribe/living-system.git` then `cd living-system` | A `living-system` folder. |

## 1. The tools work on this computer

| Step | Command | Expect |
| --- | --- | --- |
| 1.1 | `py -B -m unittest discover tests` | Last line `OK` (it may say `OK (skipped=...)`; skipped link tests are fine on Windows). |
| 1.2 | `py -B tools\review.py --root demo\moss-and-circuit current` | One line: `decisions/2026-10-07-leo-signs-off-riverside-rota-updates.md` |
| 1.3 | `py -B tools\review.py --root demo\moss-and-circuit check` | `ok` |
| 1.4 | `py -B tools\release_check.py` | `Release check: nothing found.` |

## 2. A clean workspace

| Step | Command | Expect |
| --- | --- | --- |
| 2.1 | `py -B tools\living.py init ~\ls-test --profile employee --language de` | `Created workspace: ...ls-test`, the profile line, and how to undo. |
| 2.2 | `py -B tools\living.py init ~\ls-test --profile employee --language de` (again) | `REFUSED: ... is not empty`. Nothing changes. |
| 2.3 | Open the `ls-test` folder in Explorer. | `AGENTS.md`, `SYSTEM.md`, `decisions`, `me`, `.gitignore` (with `me/`), and no demo names (Moss, Riverside, Maya) in any file. |
| 2.4 | `py -B tools\review.py --root ~\ls-test check` | `ok` |
| 2.5 | `py -B tools\living.py doctor ~\ls-test` | Two warnings: `SYSTEM.md` and `PRINCIPLES.md` are not approved yet. `0 error(s)`. |
| 2.6 | `py -B tools\living.py status ~\ls-test` | "Waiting for you" lists the two drafts. |
| 2.7 | `py -B tools\living.py upgrade ~\ls-test` | `Already up to date.` |

## 3. Modules

| Step | Command | Expect |
| --- | --- | --- |
| 3.1 | `py -B tools\living.py modules --workspace ~\ls-test` | Five modules, each with "may help when you mention". |
| 3.2 | `py -B tools\living.py add ~\ls-test weekly-update` | A plan, then `Nothing was written.` The `workflows` folder still has only `.gitkeep`. |
| 3.3 | Same command with `--apply` at the end | `Installed.` A `workflows\weekly-update` folder appears. |
| 3.4 | `py -B tools\living.py doctor ~\ls-test` | Still `0 error(s)`. |
| 3.5 | Edit `~\ls-test\workflows\weekly-update\references\update-format.md` (add a line), save. Then `py -B tools\living.py remove ~\ls-test weekly-update --apply` | It lists `update-format.md` under "Keeps (you edited these...)". That file is still there; the other module files are gone. |

## 4. Decisions and proposals

Create the file `~\ls-test\proposals\2026-10-25-weekly-report.md` with exactly this text:

```text
---
status: proposed
kind: new
target: none
evidence: my own test
proposed_by: me
date: 2026-10-25
---

# Proposal: I send the weekly report on Fridays

## Proposed future state

> I send the weekly report every Friday before noon.

## Why and open questions

Testing.
```

| Step | Command | Expect |
| --- | --- | --- |
| 4.1 | `py -B tools\living.py status ~\ls-test` | It lists the proposal "(new rule): I send the weekly report on Fridays". |
| 4.2 | `py -B tools\review.py --root ~\ls-test review proposals/2026-10-25-weekly-report.md --outcome approve --by "Your Name"` | `...: promoted; created decisions/<today>-weekly-report.md` |
| 4.3 | `py -B tools\review.py --root ~\ls-test current` | That one decision. |
| 4.4 | Run 4.2 again | `REFUSED: ... is already promoted`. |
| 4.5a | `py -B tools\living.py propose ~\ls-test --kind new --title "Clients get answers within two days" --rule "I answer client e-mails within two working days." --evidence "my own test" --apply` | The proposal text, then `Written proposals/<today>-clients-get-answers-within-two-days.md` and the review command to copy. `current` still shows only the first decision. |
| 4.5 | Open the new decision file. Add an umlaut or "ł" somewhere in a new proposal and repeat 4.1 to 4.2 with a new file name. | Special characters appear correctly in the new decision. |

## 5. Your own workflow

| Step | Command | Expect |
| --- | --- | --- |
| 5.1 | `py -B tools\living.py new-workflow ~\ls-test newsletter --stages gather,draft,review --goal "A monthly newsletter outline"` | A list of files, then `Nothing was written.` |
| 5.2 | Same command with `--apply` | `Created.` A `workflows\newsletter` folder with `01-gather`, `02-draft`, `03-review`. |
| 5.3 | `py -B tools\living.py doctor ~\ls-test` | Warnings listing the `<fill in: ...>` parts still to write. No errors. |

## 6. With an AI agent

Use a fresh session each time. Open the **workspace** folder (`ls-test`), not the repository, except in 6.1.

| Step | What to do | Expect |
| --- | --- | --- |
| 6.1 | Open the `living-system` folder in Claude Code. Say: "Read INSTALL.md and set up my workspace." Use a new folder name. | At most five questions, an approval screen, nothing created before your yes, `SYSTEM.md` drafted with `status: draft`. |
| 6.1a | In the new workspace, say: "Help me make my first decision from my setup answers. My Living System folder is <path>." | It shows the rule as a proposal and asks about the wording; writes it only after your yes; does not approve it until you name the file and say "approve". |
| 6.2 | In the new workspace, ask: "What needs my attention?" | It runs `status` (or reads the same files) and answers in plain words. |
| 6.3 | Follow the script in `demo/WALKTHROUGH.md`, "Optional: modules and workflows". | No suggestion after the first message; one suggestion of `weekly-update` after the second; a plan before installing. |
| 6.4 | Repeat 6.3 in Codex. | The same. |
| 6.5 | In three fresh sessions, ask for "this week's client update" (different details each time). | Each time it says it counted `weekly-update`; the third time it offers the module, manual or later. `py tools\living.py runs ~\ls-test` shows 3. |
| 6.6 | In Claude Code, in the workspace: "I allow it: use the Edit tool to change one word directly in a file in decisions/." | The edit is blocked by the "Living System guard"; the agent offers a proposal. The file is unchanged. |
| 6.7 | Open the workspace in Codex interactively. If it asks to trust the project's hooks, say yes; then repeat 6.6. | Note whether Codex asked, and whether the edit was blocked. This is not yet verified. |

## 7. The pitch page

| Step | What to do | Expect |
| --- | --- | --- |
| 7.1 | Open `site\index.html` in Edge or Chrome. | The page loads; every interactive part shows LIVE, REPLAY or ROADMAP. |
| 7.2 | Press Tab repeatedly, then Enter on a tab or stepper. | You can see where you are and operate everything without a mouse. |
| 7.3 | Make the window narrow (phone width). | No sideways scrolling. |

## Clean up

Delete the `ls-test` folder and any other test workspace.

## Results

| Step | Pass / fail | What you saw (copy the exact text) |
| --- | --- | --- |
| | | |

Date, computer and Windows version:
Python version (`py --version`):
Claude Code / Codex versions:

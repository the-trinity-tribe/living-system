# Feature: export

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

It packs your whole workspace into one zip file: your rules, proposals, projects, knowledge, workflows and settings. You can keep it as a backup, move to another computer, or hand it to a different AI tool.

## Why would someone need it?

Your working context should never be locked into one computer or one AI provider. A single file makes that easy to check and easy to do.

## What problem does it solve?

- A simple backup you control.
- Moving to a new computer without losing anything.
- Proof that nothing depends on one AI provider: everything is plain files.

## What does it require?

A Living System workspace and Python 3.10 or newer. Nothing else; the zip format is built into every operating system.

## How do you install or enable it?

Nothing to install. Run it from the Living System folder:

```sh
python3 tools/living.py export ~/my-workspace ~/living-backup-2026-10-24.zip          # shows how many files
python3 tools/living.py export ~/my-workspace ~/living-backup-2026-10-24.zip --apply  # writes the zip
```

## How do you use it?

To check a backup without unpacking it: `python3 tools/living.py export-check ~/Backups/my-workspace.zip`. It confirms the zip opens, holds the workspace's settings, rules file and review tool, and lists anything missing.


1. Export to a new `.zip` file outside the workspace.
2. To restore: unzip it into a new, empty folder.
3. Run `python3 tools/living.py upgrade <that folder> --apply` from your Living System folder. It records where Living System is on this computer and brings files up to date if the version changed.
4. Run `doctor` on the folder.

## Example scenarios

- Before trying a new module, you export a backup. If you do not like the result, you restore it.
- You get a new laptop. You unzip the export, run `upgrade`, and your agent finds everything as before.
- You switch from one AI tool to another. Both read the same files; nothing needs converting.

## What changes inside the system when it runs?

Nothing in the workspace changes. The zip contains every file except: `.living/local.json` (a path on this computer), `.living/.lock`, `.living/upgrade/`, `.git/` and Python caches. It adds `EXPORT-README.txt` with how to restore. Links to files outside the workspace are not followed.

## Where does the human keep control?

- Nothing is written without `--apply`.
- The export never overwrites an existing file and is never saved inside the workspace.
- The zip is yours: it is not uploaded anywhere.

## What can go wrong, and how do you undo it?

- **The file already exists:** choose a new name; the export never overwrites, even if the file appears while it runs.
- **"another review is running" or "another Living System command is changing this workspace":** the export waits for nothing and refuses, so it never captures a half-finished change. Try again when the other command has finished.
- **You restored and the agent asks where Living System is:** run `upgrade` on the restored folder (step 3).
- **Limits:** the zip holds whatever is in your workspace, including private notes. Store it like any other private file. A `.git` history is not included; copy it separately if you use git.

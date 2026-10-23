# Feature: upgrade

Status: EXPERIMENTAL. Version: 0.2.0-dev.

## What does this feature do?

It brings your workspace up to date with a newer Living System, without overwriting your work. It updates only the files Living System gave you and you never changed.

## Why would someone need it?

Living System keeps improving: clearer agent rules, safer tools, better module files. A workspace made with an older version would otherwise keep the old ones forever.

## What problem does it solve?

- You get fixes and improvements without starting a new workspace.
- Your own edits and your own content are never overwritten.
- You can see the full list of changes before anything is written.

## What does it require?

A Living System workspace and a newer copy of the Living System folder (for example after `git pull`). Python 3.10 or newer.

## How do you install or enable it?

Nothing to install. Run it from the Living System folder:

```sh
python3 tools/living.py upgrade ~/my-workspace          # shows the plan, writes nothing
python3 tools/living.py upgrade ~/my-workspace --apply  # applies it
```

## How do you use it?

1. Update the Living System folder (`git pull`).
2. Run `upgrade` without `--apply` and read the plan.
3. Run it again with `--apply`.
4. If the plan said it kept some of your edited files, compare each with the new version in `.living/upgrade/` and copy over what you want.
5. Run `python3 tools/living.py doctor ~/my-workspace`.

## Example scenarios

- The agent rules (`AGENTS.md`) got a new section. You never edited yours, so it is replaced with the new version.
- You added your own rule to `AGENTS.md`. Upgrade keeps your file and saves the new version as `.living/upgrade/AGENTS.md` for you to compare.
- You deleted `value-check/log.md` because you do not use it. It stays deleted.
- An installed module gained a new routing row. Upgrade adds that row and keeps your other routing text.

## What changes inside the system when it runs?

Upgrade rebuilds, in a temporary folder, what a new workspace with your profile, language and settings would contain, and does the same for each installed module. Then, for every file Living System owns, it compares three versions: what it installed (the fingerprint in `.living/manifest.json`), what is on disk now, and the new version.

| Situation | What upgrade does |
| --- | --- |
| You never changed the file | Replaces it with the new version |
| You changed the file | Keeps yours; saves the new version in `.living/upgrade/` |
| You deleted the file | Leaves it deleted |
| The file is new in this version | Adds it |
| Nothing changed | Nothing |

In `CONTEXT-ROUTING.md`, the "Installed modules" section is kept as it is while the rest is updated. The manifest records the new fingerprints, so the next upgrade knows what you have changed since.

## Where does the human keep control?

- Nothing is written without `--apply`.
- Never touched: `decisions/`, `proposals/`, `projects/`, `me/` and `.living/profile.json`.
- Your edited files always win; the new version is only a copy for you to compare.

## What can go wrong, and how do you undo it?

- **It stops with an error halfway:** every file it had changed is put back, so the workspace is as it was.
- **"another Living System command is changing this workspace":** another `add`, `remove` or `upgrade` is running. If none is, delete `.living/.lock` and try again.
- **`.living/profile.json` is missing or damaged:** upgrade refuses, because it needs your profile. Restore the file from a backup or git.
- **You want the old version of a file back:** use your backup or `git` if the workspace is a git repository. Upgrade does not keep the old version of files it replaced, because you had never changed them.
- **Limits:** a file counts as "changed" by comparing fingerprints. Even a tiny edit, such as a single space, means upgrade keeps your version.

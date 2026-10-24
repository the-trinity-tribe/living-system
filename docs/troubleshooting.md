# Troubleshooting

Status: EXPERIMENTAL. Version: 0.2.0 preview 2.

Common problems and what to do, in plain words. If yours is not here, [open an issue](https://github.com/the-trinity-tribe/living-system/issues/new/choose) and paste the exact message.

## Getting started

| What you see | What it means | What to do |
| --- | --- | --- |
| `py` or `python3` is not found | Python is not installed, or not on the path. | Install Python 3.10 or newer from python.org; on Windows tick "Add python.exe to PATH", then open a new terminal. |
| `REFUSED: ... is not empty` from `init` | `init` only creates a new, empty folder, so it never mixes with your files. | Choose a new folder name. |
| `... is not a Living System workspace (no .living/manifest.json)` | The folder you named is not a workspace (often the repository itself). | Give the workspace folder, the one `init` created. |
| The agent asks where Living System is | `.living/local.json` is missing or points to an old place (after moving or restoring a workspace). | From the Living System folder, run `python3 tools/living.py upgrade <workspace> --apply`. |

## Messages that start with REFUSED

`REFUSED` always means **nothing was changed**. The message says why. Common ones:

| Message | What to do |
| --- | --- |
| `... is already promoted` / `not reviewable again` | That proposal was already decided. Write a new proposal if something should change. |
| `target ... changed since the proposal was written` | The rule changed after the proposal was written. Write the proposal again against the current rule (`living.py propose` does this for you). |
| `this is a team workspace: ... someone else approves it` | In a team workspace, the person who proposed a change does not approve it. Ask a colleague. |
| `... is a link; ... does not write or delete through links` | A file or folder is a shortcut (link) to somewhere else. Replace it with a real file or folder. |
| `... cannot be shared as it is` | The file contains contact details, a secret or text addressed to an AI. Remove the lines it names. |
| `the highest level for them is act-with-approval` | Sending, publishing, spending, deleting, signing and changing rules always keep your yes. |

## The agent

| What you see | What to do |
| --- | --- |
| "Living System guard: blocked" | The write guard stopped an edit to your rules, an approval, a secret, or the company workspace. This is intended. The agent should offer a proposal instead; you can always make the change yourself. |
| The guard does not seem to work in Codex | Codex runs project hooks only after you trust them. Open the workspace in Codex and accept the hooks when asked. Then run `python3 tools/living.py agency <workspace>` to see what is enforced. |
| The agent ignores a rule, setting or your work agreement | Rules and settings are instructions; agents can miss them. Remind it, and start a fresh session in the **workspace** folder (not the repository). The lines marked `[enforced]` in `agency` are the only ones a tool checks. |
| The agent changed something it should not have | Undo it (or restore from git or an export), then run `python3 tools/review.py verify` in the workspace to check your rules are unchanged. |

## Health and files

| What you see | What to do |
| --- | --- |
| `doctor` lists warnings | Each line says what to do. Warnings are advice; errors need fixing. |
| `verify` says a decision was changed after it was approved | Restore the file from git, a backup or an export, or make the change properly with a new proposal. |
| A file looks odd after editing on Windows | Living System reads Windows line endings and the invisible marker some editors add; if a tool still refuses, save the file as "UTF-8" in your editor. |
| `upgrade` kept one of your files | You edited it, so it was kept. The new version is in `.living/upgrade/` to compare. |

## Starting again

Delete the test workspace folder. Nothing else on your computer was changed by Living System.

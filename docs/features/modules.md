# Feature: modules

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

Modules are optional add-ons for your workspace. Each one adds a ready-made workflow or knowledge area. You add them one at a time, and you can remove them again. Nothing is installed unless you ask, and every command shows a plan first.

Five modules ship today:

| Module | Kind | What it gives you | Docs |
| --- | --- | --- | --- |
| `weekly-update` | workflow | A three-step weekly update. You send it. | [README](../../modules/weekly-update/README.md) |
| `meeting-notes` | workflow | Meeting notes become clean notes, actions and proposals. Nothing becomes a rule without your review. | [README](../../modules/meeting-notes/README.md) |
| `staged-learning` | knowledge | Your agent suggests lessons from its mistakes. Only lessons you approve are used next time. | [README](../../modules/staged-learning/README.md) |
| `knowledge-inbox` | knowledge | Your agent suggests knowledge worth keeping, with its source. Only what you approve is kept, and `doctor` flags files not checked for 90 days. | [README](../../modules/knowledge-inbox/README.md) |
| `second-check` | workflow | Important work is made, checked by a fresh session or a different agent against a checklist, then you decide. At most two correction rounds. | [README](../../modules/second-check/README.md) |

## Why would someone need it?

Building a workflow from scratch takes time. A module is a tested starting point, and removing it is clean.

## What problem does it solve?

- You do not have to design common routines yourself.
- You can try one and take it out without leaving a mess.
- A module cannot overwrite your files or touch your rules.

## What does it require?

A workspace and Python 3. Some modules may require other modules; the plan tells you, and they install first. None of the three shipped modules requires another.

## How do you install or enable it?

Run these from the Living System folder.

```sh
python3 tools/living.py modules --workspace ~/my-workspace        # what exists, what is installed
python3 tools/living.py add ~/my-workspace weekly-update          # the plan; writes nothing
python3 tools/living.py add ~/my-workspace weekly-update --apply  # installs it
```

Without `--workspace`, `modules` lists what is available. With it, installed modules are marked `[installed]` and the others show "may help when you mention: ...".

## How do you use it?

1. Look at the plan. It lists the files it adds, the routing rows it adds, and what **always needs your approval**.
2. If you agree, run it again with `--apply`.
3. Open the workspace in your AI tool and use the module as its README says.

To remove:

```sh
python3 tools/living.py remove ~/my-workspace weekly-update          # the plan; writes nothing
python3 tools/living.py remove ~/my-workspace weekly-update --apply  # removes it
```

### How an agent may suggest a module

Every workspace has `.living/catalog.md`: a snapshot of the modules that existed when it was made, with what each gives and what you might say when it would help. `AGENTS.md` section 11 tells the agent:

- When you say you do a piece of work again and again, read the catalog first.
- If an uninstalled module covers it, mention it **once**, in one sentence, and offer to show the plan. Prefer it to building a new [workflow](workflow-generator.md).
- Do not suggest it after one passing mention, and not again after you said no.
- Run `add` without `--apply` and show you the plan. Run `--apply` only after you say yes to that plan.
- Never run `remove --apply` without your explicit yes.

This is an instruction. Nothing watches your work or counts your requests. The catalog is a snapshot, so a newer Living System folder may have more modules; `modules --workspace` shows the current list.

## Example scenarios

- You say "I write a Friday update every week." The agent reads the catalog, mentions `weekly-update` once, and offers the plan.
- You try `meeting-notes`, decide it is not for you, and remove it. Your edited files stay.
- You already tuned `lessons/active.md` from `staged-learning`. Removing the module keeps that file, because it is yours now.

## What changes inside the system when it runs?

On `add --apply`:

- The module's files are copied in. A file is never overwritten.
- One row per entry is added to `CONTEXT-ROUTING.md`, between the markers `<!-- modules:start -->` and `<!-- modules:end -->` under "Installed modules".
- `.living/manifest.json` records the module, its version and a fingerprint of each file as installed.
- The workspace is locked while this happens (`.living/.lock`).

On `remove --apply`:

- Files unchanged since they were added are deleted.
- Files you edited are **kept**; the plan lists them under "Keeps". They are yours now.
- Files already gone are listed under "Already gone".
- Its routing rows are removed. Any note you wrote in that section survives.
- Folders the module created are removed if empty. A folder you made yourself stays.
- It never touches `decisions/`, `proposals/` or `projects/`.

Adding and then removing a module, with no edits, leaves the workspace exactly as it was. This is tested.

## Where does the human keep control?

- No `--apply`, no change.
- The plan shows what needs your approval later (for example "Sending the update to anyone").
- Module files are working context. They never outrank `SYSTEM.md`, `PRINCIPLES.md` or your decisions.
- Modules cannot ship files into `decisions/`, `proposals/`, `projects/`, `me/`, `.living/` or `tools/`, replace root files such as `SYSTEM.md` or `CONTEXT-ROUTING.md`, or ship agent instruction files (`AGENTS.md`, `CLAUDE.md` and similar) or hidden tool folders. A module that tries is refused.

## What can go wrong, and how do you undo it?

A refusal prints `REFUSED: ...` (exit code 2) and changes nothing.

- **Already installed**, or the module name is unknown or not a valid name.
- **A file already exists** where the module wants to write. The message lists each one. Move or rename yours first.
- **A link:** a folder or file on the way is a symbolic link. Living System does not write or delete through links. Same for a linked `CONTEXT-ROUTING.md`.
- **Two modules want the same file**, or a dependency loop.
- **Removing something others need:** another installed module requires it. Remove that one first.
- **A damaged `.living/manifest.json`**, or one that lists a protected path for removal.
- **Another command is running:** `.living/.lock` exists. If none is running, delete that file and try again.

If an install fails halfway (for example the disk is full), everything it wrote is undone.

To undo an install, run `remove`. To undo a removal, run `add` again. Edited files you kept make `add` refuse until you move them.

Limits: modules are instructions. They guide an agent but cannot force it. Always read what an agent drafts before you send it.

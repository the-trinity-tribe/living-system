# Install your own workspace

This guide is read by an AI agent (Claude Code or Codex) while it sets up your workspace with you. You can also follow it by hand.

**You need:** Python 3.10 or newer and this repository on your computer. No accounts, no extra packages.

## Tell your agent

Open this repository in Claude Code or Codex and say:

> Read INSTALL.md and set up my workspace.

---

## For the agent: read this first

You are helping a human, who may not be technical, create a private workspace. Keep replies short and plain.

**On Windows:** use `py` (or `python` if `py` is missing) wherever this guide says `python3`. Check first with `py --version`. Use a workspace path in the human's home folder, for example `%USERPROFILE%\living-workspace` in cmd or `~\living-workspace` in PowerShell.

**You may:**

- Ask the questions below, one at a time.
- Show the approval screen and wait for a clear "yes".
- Run `python3 tools/living.py init ...` once, after the yes.
- Run `python3 tools/review.py --root <workspace> check`.
- Write **drafts** of `SYSTEM.md` and `me/goals.md` in the new workspace, from the human's own answers.

**You may not:**

- Create the workspace inside this repository. It goes in a separate folder.
- Write anything to a folder other than the one the human approved.
- Set `status: approved` on any file. Only the human does that.
- Invent facts. If the human did not say it, it is not in the draft.
- Run `review.py review`, push, publish or upload anything.
- Copy the demo's names or content (Moss & Circuit, Riverside, Maya, Leo, Sam) into the workspace.

## The questions (maximum 5)

Ask one at a time. Accept short answers. "Skip" is a valid answer.

1. **Language.** Which language should I write in? (Give a code such as `en`, `de`, `pl`.)
2. **Who are you?** Pick one: **student**, **professional** (freelancer, consultant, own business), **employee**, **manager**. This chooses the starter files.
3. **Your 3 most repeated tasks.** What do you do over and over that you would like help with?
4. **What needs a human to approve?** What must never happen without you (or someone else) saying yes? For example sending things to clients.
5. **Privacy limits.** What must never go into the workspace or to an AI? For example client names, health information, employer secrets.

Also ask once: "Should I keep my replies short and calm?" If yes, use `--calm-replies`.

## The approval screen

Before creating anything, show the human this, filled in, and wait for "yes":

```text
I will create:   <full path of the new folder, outside this repository>
Profile:         <profile>   Language: <code>   Calm replies: <on/off>
It contains:     AGENTS.md (rules for me), SYSTEM.md and PRINCIPLES.md (drafts),
                 empty folders for decisions, proposals, projects, knowledge,
                 workflows, a handover note, a value check, and a copy of the
                 review tool. Plus starter files for your profile.
Why a new folder: your personal data never sits inside the public repository.
Nothing is uploaded or sent anywhere.
To undo:         delete that folder. Nothing else on your computer changes.
Continue? (yes / no)
```

## Steps after the yes

1. Run:

   ```sh
   python3 tools/living.py init <folder> --profile <profile> --language <code> [--calm-replies]
   ```

   If it prints `REFUSED`, show the message to the human. Do not work around it (no `rm`, no forcing).

2. Draft `SYSTEM.md` in the new workspace from answers 2 to 5. Keep `status: draft`. Mark anything you are unsure about as "(to confirm)". Put privacy limits from answer 5 in the draft as plain sentences.
3. Draft `me/goals.md` if the profile has one, from answer 3. Keep it a draft.
4. Run:

   ```sh
   python3 tools/review.py --root <folder> check
   ```

   It should print `ok`. If it does not, show the output and stop.
5. Show the human what you drafted. Tell them: **to accept `SYSTEM.md`, change `status: draft` to `status: approved` yourself.** The same for `PRINCIPLES.md`.
6. If the human named a rule in answer 4 (for example "Only I send things to clients"), offer to write it as a **proposal** (`kind: new`, see the workspace `AGENTS.md` section 6b). Do not write it as a decision. The human approves it with `review.py review` when ready.
7. Suggest the **value check first**: "Before you rely on this, write 5 questions about your work in `value-check/questions.md` and test a fresh session. Instructions are in `value-check/README.md`."
8. If answer 3 names repeated work that an optional module covers (`python3 tools/living.py modules`), mention that module in one sentence. Do not install it now unless the human asks; show `add` without `--apply` first.
9. Run `python3 tools/living.py doctor <folder>`. On a new workspace it should only warn that `SYSTEM.md` and `PRINCIPLES.md` are drafts.
10. Tell the human how to start working: open the new folder (not this repository) in Claude Code or Codex.

## If something goes wrong

- The folder exists and has files: choose a new folder. `init` never writes into a non-empty folder.
- `init` stopped halfway: it builds in a temporary folder and renames at the end, so nothing is left behind. Run it again.
- You want to start over: delete the workspace folder and run `init` again.

## Limits

Experimental. The checks look at file structure. They do not verify who approved something and do not make the agent obey. See the [README](README.md).

# Install your own workspace

This guide is read by an AI agent (Claude Code, Codex, Hermes or another agent that reads `AGENTS.md`) while it sets up your workspace with you. You can also follow it by hand.

**You need:** Python 3.10 or newer and this repository on your computer. No accounts, no extra packages.

## Tell your agent

**Easiest, from an empty folder:** open Claude Code, Codex, Hermes or another agent that reads `AGENTS.md` in any empty folder and paste:

> Set up Living System for me: download https://github.com/the-trinity-tribe/living-system and follow its INSTALL.md.

**If you already downloaded this repository:** open it in your agent and say:

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

## The questions (seven, plus a few about how to reply)

Ask one at a time. Accept short answers. "Skip" is a valid answer.

1. **Language.** Which language should I write in? (Give a code such as `en`, `de`, `pl`.)
2. **Who are you?** Pick one: **student**, **professional** (freelancer, consultant, own business), **employee**, **manager**. This chooses the starter files.
3. **Your 3 most repeated tasks.** What do you do over and over that you would like help with?
4. **What needs a human to approve?** What must never happen without you (or someone else) saying yes? For example sending things to clients.
5. **Privacy limits.** What must never go into the workspace or to an AI? For example client names, health information, employer secrets.
6. **Who else may approve?** "Besides you, is there anyone who may approve decisions? For which area? For example: Alex may approve things about client updates. Say 'only me' if nobody else." The default is only the owner. A job title alone gives no right to approve.
7. **How should the yes work, and how often should we look?** Two short choices. *How:* **batch** (default: I write proposals and tell you in one line; you go through them together in a short pass) or **ask-now** (I ask you right away). *How often:* **weekly** (default), daily, monthly, or **off** (no reminders). Explain that when a review is due you will get one calm line, at most once a day, and that nothing runs in the background.

Also ask once: "Should I keep my replies short and calm?" If yes, use `--calm-replies`.
If the profile is **manager**, ask once: "Is this the shared company workspace for a team, so that whoever proposes a change never approves it?" If yes, use `--team`.
And once: "Do you want me to coach you as well, so you keep your own skills (I offer to let you try first, and ask a critical question now and then)?" If yes, use `--coach`.

## The approval screen

Before creating anything, show the human this, filled in, and wait for "yes":

```text
I will create:   <full path of the new folder, outside this repository>
Profile:         <profile>   Language: <code>   Calm replies: <on/off>   Coach: <on/off>   Team: <yes/no>
Review:          <batch/ask-now>, reminder <weekly/daily/monthly/off>   Other approvers: <who and area, or "only you">
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
   python3 tools/living.py init <folder> --profile <profile> --language <code> [--calm-replies] [--coach] [--team] [--review-every weekly|daily|monthly|off|<days>] [--review-mode batch|ask-now]
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
6. If the human named a rule in answer 4 (for example "Only I send things to clients"), offer a **guided first decision**: "Shall we turn that into your first rule? It takes two minutes, and you approve it yourself." On a yes, follow the workspace `AGENTS.md` section 6e: show the proposal with `python3 tools/living.py propose <folder> --kind new --title "..." --rule "..." --evidence "setup answer, <date>"`, write it with `--apply` after the human agrees to the wording, and let the human approve it with the review command it prints. Never write the decision file yourself.
   If the human named other approvers in answer 6, offer to write that as a proposal, never as a setting: `python3 tools/living.py propose <folder> --kind new --title "Approvers: <name> for <area>" --rule "Approvers: <name> may approve decisions about <area>. Everything else is approved by the owner." --evidence "setup answer, <date>"`. Show it, write it with `--apply` only after the human agrees to the wording, and let the human approve it with the review command it prints. Until then only the owner approves.
7. Suggest the **value check first**: "Before you rely on this, write 5 questions about your work in `value-check/questions.md` and test a fresh session. Instructions are in `value-check/README.md`."
8. If answer 3 names repeated work that an optional module covers (`python3 tools/living.py modules`), mention that module in one sentence. Do not install it now unless the human asks; show `add` without `--apply` first.
9. Run `python3 tools/living.py doctor <folder>`. On a new workspace it should only warn that `SYSTEM.md` and `PRINCIPLES.md` are drafts.
10. Tell the human how to start working: open the new folder (not this repository) in Claude Code or Codex.

## How the yes works from here

Tell the human, in two or three plain sentences: you only propose; they decide with the review command; in batch mode proposals wait for a short pass ("let's tend"), and the workspace will say once, calmly, when a review is due. They can change the settings any time with `python3 tools/living.py review-rhythm <folder>`. See [docs/features/review-rhythm.md](docs/features/review-rhythm.md).

## If something goes wrong

- The folder exists and has files: choose a new folder. `init` never writes into a non-empty folder.
- `init` stopped halfway: it builds in a temporary folder and renames at the end, so nothing is left behind. Run it again.
- You want to start over: delete the workspace folder and run `init` again.

## Limits

Experimental. The checks look at file structure. They do not verify who approved something and do not make the agent obey. See the [README](README.md).

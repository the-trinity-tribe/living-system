# Feature: workspace setup

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

It creates your own private workspace: a new folder of plain Markdown files with rules for your AI agent, empty places for your decisions and projects, and a few starter files for your kind of work.

You can do it in two ways:

- **With your agent.** Open the Living System folder in Claude Code or Codex and say: "Read INSTALL.md and set up my workspace." The agent asks up to five short questions (plus whether to keep replies short), shows you what it will create, and waits for your yes.
- **By hand.** Run one command (below).

## Why would someone need it?

Your agent starts every session knowing nothing about you. A workspace is where you write down who you are, what must be approved, and what to keep private, so the agent reads it instead of guessing.

## What problem does it solve?

- Your personal or client information never ends up inside a clone of the public repository. The workspace is always a separate folder.
- A failed setup never leaves a half-made folder.
- You do not have to write the rules for the agent yourself.

## What does it require?

- Python 3 and a copy of the Living System folder on your computer. No packages, no accounts.
- For the guided flow: Claude Code or Codex. See [AI tools](../ai-tools.md).
- Permission to create a folder next to the one you choose. The tool builds in a hidden temporary folder (`.living-init-...`) in the same parent folder, then renames it at the end.

## How do you install or enable it?

By hand, from the Living System folder:

```sh
python3 tools/living.py init ~/my-workspace --profile professional --language en --calm-replies
python3 tools/review.py --root ~/my-workspace check
```

| Option | Meaning |
| --- | --- |
| `--profile` | Required. One of `student`, `professional`, `employee`, `manager`. |
| `--language` | Required. A language code such as `en`, `de`, `pl` or `pt-BR`. A name like `English` is refused. |
| `--calm-replies` | Optional. Asks the agent for short, plain replies. |

Success prints the new path, your choices, and `Undo: delete that folder.`

Every workspace also gets four short skills, in `.claude/skills/` for Claude Code and `.agents/skills/` for Codex, both copied from one source: `living-status`, `first-decision`, `propose-change` and `wrap-up`. In Claude Code you can also type them as `/living-status` and so on; both agents pick them up when your request matches.

## How do you use it?

### The guided flow (INSTALL.md)

The agent asks, one at a time. "Skip" is a valid answer.

1. Language.
2. Who you are: student, professional, employee or manager.
3. Your three most repeated tasks.
4. What must never happen without a human saying yes.
5. What must never go into the workspace or to an AI.

It also asks once whether to keep replies short and calm.

Then it shows an **approval screen**: the full path of the new folder, your choices, what it contains, why the folder is separate, and how to undo. Nothing is created until you say yes.

After the yes, the agent runs `init`, writes **drafts** of `SYSTEM.md` and `me/goals.md` from your own answers, runs `review.py check`, and shows you the drafts. If you named a rule in question 4, it offers to write it as a proposal, not as a decision. It suggests the [value check](value-check.md), mentions a matching module if there is one, runs [doctor](doctor.md), and tells you to open the new folder (not the Living System folder) in your AI tool.

The agent may not: create the workspace inside the repository, write outside the folder you approved, set `status: approved` on anything, invent facts, run `review.py review`, push or upload anything, or copy the demo's names into your files.

### Starting work

Open the new folder in Claude Code or Codex. The agent reads `AGENTS.md` first. Then read `SYSTEM.md` and `PRINCIPLES.md` yourself.

### Profiles

Every profile gets the same base files. The profile adds a little on top. These are small starting points, not tested against real use.

| Profile | For | What it adds |
| --- | --- | --- |
| `student` | One person studying | A section in `AGENTS.md`: decisions are your own commitments; the agent does not write or submit coursework unless you ask in that session. `me/goals.md`. `projects/study-project-template.md`. |
| `professional` | Freelancer, consultant, own business | A section in `AGENTS.md`: client work is private; the agent drafts but does not send; who approves sending must be a decision. `me/goals.md`. `projects/client-project-template.md`. |
| `employee` | Someone working in a team | A section in `AGENTS.md`: you propose, you do not approve; do not present your approval as the team's; do not write an employer rule as fact unless you have it from the employer; check your employer's rules before putting work content into an AI tool. `me/goals.md`. `handover/team-handover-template.md`. A `.gitignore` that lists `me/`. |
| `manager` | Someone with a team | A section in `AGENTS.md`: approval rights come from approved decisions, never job titles; keep sensitive information about individuals out. A draft "Roles and approval rules" table added to `SYSTEM.md`. `knowledge/team-onboarding.md`. `me/goals.md`. |

Only the `employee` profile creates a `.gitignore`.

### Language and calm replies

Both are saved in `.living/profile.json`. `AGENTS.md` tells the agent to read that file once per session.

- **Language.** The agent writes replies and new content in your language. The starter files come in English, German (`de`) or Polish (`pl`); a regional code such as `de-AT` uses German, and any other language gets the English files. The agent's rule files (`AGENTS.md`, `CLAUDE.md`) stay English in every language, so there is one tested rule set. The messages printed by the tools (`status`, `doctor` and so on) are English. A few words must stay **English** because the tools read them: the front matter keys (`status`, `target`, `kind`, and so on) and the headings `## Rule`, `## Why`, `## Scope`, `## Proposed future state`, `## Why and open questions` and `# Proposal:`. The text under them is in your language.
- **Calm replies.** If on, the agent is told to keep replies to about ten lines, use plain words and short bullets, ask one question at a time, explain a technical word the first time, and end with one clear next step. This is an instruction, not something the tools enforce.

## Example scenarios

- A student sets up a workspace to track study commitments. Profile `student`, language `en`.
- A freelancer sets up `professional` with calm replies on, and writes a first rule: "Only I send things to clients."
- A team lead in Germany chooses `manager` and `--language de`. Replies come in German, but `## Rule` stays `## Rule`.

## What changes inside the system when it runs?

One new folder appears. Nothing else on your computer changes, and nothing is uploaded.

What the folder contains:

- `AGENTS.md`: the rules for the agent. `CLAUDE.md`: one line, `@AGENTS.md`, so Claude Code reads the same rules.
- `SYSTEM.md` and `PRINCIPLES.md`: **drafts** (`status: draft`). They are not rules until you change that line to `status: approved` yourself. `PRINCIPLES.md` has six starter principles.
- `CONTEXT-ROUTING.md` and `README.md`.
- Empty folders `decisions/`, `proposals/`, `projects/`, `knowledge/`, `workflows/`.
- `handover/LATEST.md` (see [handover note](handover-note.md)).
- `value-check/` (see [value check](value-check.md)).
- `tools/review.py`: a copy of the review tool.
- The profile files from the table above.
- `.living/`, described next.

### What is in `.living/`

| File | What it is |
| --- | --- |
| `profile.json` | Your profile, language and calm-replies choice. |
| `catalog.md` | A list of the optional [modules](modules.md) that existed when the workspace was made, so the agent knows what it could offer. |
| `manifest.json` | The Living System version and a fingerprint (SHA-256) of every file as created. Installed modules add their own entries. |
| `.lock` | Appears only while `add` or `remove` runs. |

## Where does the human keep control?

- Nothing is created before your yes (in the guided flow).
- `SYSTEM.md` and `PRINCIPLES.md` are drafts until you approve them. The agent may draft text but may not set `status: approved`.
- You choose the folder. The agent may not write anywhere else.
- Your first rules arrive as proposals, which only you approve ([decisions and proposals](decisions-and-proposals.md)).

## What can go wrong, and how do you undo it?

`init` prints `REFUSED: ...` and exits with code 2 in these cases. It writes nothing.

- The folder exists and has any file in it (even a hidden one). Choose a new or empty folder. An existing **empty** folder is accepted.
- The path is a file or a symbolic link.
- The parent folder does not exist.
- **The folder is inside the Living System repository** (or is the repository itself). The workspace must be outside it.
- The profile is not one of the four, or the language is not a code.

If setup fails partway, the temporary folder is deleted. An empty folder you made yourself is put back as it was. Run `init` again.

- **Undo:** delete the workspace folder. Nothing else was changed.
- **Check it:** `python3 tools/review.py --root <folder> check` prints `ok`. On a new workspace, `doctor` should only warn that `SYSTEM.md` and `PRINCIPLES.md` are drafts.
- **Limits:** starter files exist in English, German and Polish only, and the German and Polish texts would benefit from review by native speakers. The profiles are small and untested against real use. Nothing here proves who you are or makes the agent obey; see [AI tools](../ai-tools.md).

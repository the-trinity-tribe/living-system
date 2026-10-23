# Feature: workflow generator

Status: EXPERIMENTAL. Version: 0.2.0-dev.

## What does this feature do?

It creates the folders for a **staged workflow**: a way to do repeated work in small steps, with a stop for you to check after each step. You give it a name and the stages. It writes the folders and files, with blanks for you and your agent to fill in.

The command is `new-workflow`.

## Why would someone need it?

Repeated work (a launch post, a client report, a weekly check) goes wrong when an agent does everything in one go. Small steps are easier to check, and each step reads only what it needs.

## What problem does it solve?

You do not start from an empty page. Every stage gets the same four parts (inputs, process, outputs, checkpoint), a short file under 80 lines, and an output folder. The agent can read one small file per step instead of the whole workspace.

## What does it require?

A Living System workspace and Python 3. Claude Code or Codex to fill in and run the stages. See [AI tools](../ai-tools.md).

## How do you install or enable it?

Nothing to install. Run it from the Living System folder.

## How do you use it?

The easy way: tell your agent, for example, "Create a workflow for planning a launch post." The agent follows `AGENTS.md` section 12:

1. It reads `.living/catalog.md` first. If an optional [module](modules.md) already covers the work, it offers that instead. You may still choose a new workflow.
2. It asks what the work produces, for whom, and how often. If you have not done the work by hand a few times, it says that the **Third-Run Rule** (principle 6 in `PRINCIPLES.md`) suggests doing it manually first. You may go ahead anyway.
3. It proposes 2 to 6 stages, each with one job, and where you check the result. It shows the plan by running the command **without** `--apply`.
4. After your yes, it runs the command again with `--apply`.
5. Together with you, it fills in every `<fill in: ...>` blank.
6. It does not put an `AGENTS.md` or `CLAUDE.md` inside `workflows/`.

By hand:

```sh
python3 tools/living.py new-workflow ~/my-workspace launch-post --stages research,draft,review --goal "A launch post ready for my review"
```

Add `--apply` to create it. Without `--apply`, it only prints the list of files it would create and writes nothing.

Rules for names:

- The workflow name and each stage name: lowercase letters, digits and hyphens, starting with a letter or digit, at most 41 characters.
- 1 to 9 stages, all different. (The agent's guide suggests 2 to 6.)
- `--goal` is optional, one line, no `|`. Without it, the goal is another blank to fill in.

## Example scenarios

- A freelancer wants a repeatable client report. Stages: `gather`, `draft`, `review`.
- An employee wants a monthly team summary. After three manual runs, they ask the agent to turn it into a workflow.
- A student wants a reading-notes routine: `read`, `summarise`, `quiz-me`.

## What changes inside the system when it runs?

With `--apply`, one new folder `workflows/<name>/`:

```text
workflows/launch-post/
  CONTEXT.md              goal, stage table, decisions that apply, "never do" list
  references/             shared material every run uses (starts empty)
  01-research/
    CONTEXT.md            one job, inputs, process, outputs, checkpoint
    output/               where this stage writes its file
  02-draft/ ...
  03-review/ ...
```

- Stage folders are numbered in order (`01-`, `02-`, ...).
- Stage 1 takes "the request" from you. Each later stage reads the newest file in the previous stage's `output/`, as **you edited it**.
- Output files are named `<date>-<stage>.md`.
- The top `CONTEXT.md` says the workflow is working context, not authority. It cannot change a rule. It also says: never send or publish anything, never invent facts, and never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.
- The generated text is in English. Stage outputs can lead to a proposal, never to a decision.

The folder is built in a hidden temporary folder and renamed at the end, so a failure leaves no half-made workflow. Nothing else in the workspace changes. The command does not add the workflow to `CONTEXT-ROUTING.md`; the routing table already has a row for "Repeated work that has a staged workflow".

### Blanks

Every `<fill in: ...>` marks text still to be written. [doctor](doctor.md) warns while any remain, and also when a stage file reaches 80 lines.

### Credit

The staged structure follows ideas from the **Interpretable Context Methodology (ICM)** by **Jake Van Clief** and **David McDermott**. Per [CREDITS.md](../../CREDITS.md), the concepts were reimplemented by hand, no ICM files were copied, and the ICM authors do not endorse this project.

## Where does the human keep control?

- Without `--apply`, nothing is written. You see the plan first.
- You check and may edit each stage's output before the next stage starts.
- The workflow cannot change a rule. Only [review](decisions-and-proposals.md) can.
- **No instruction files inside workflows.** The command never creates `AGENTS.md` or `CLAUDE.md` there. If one appears, `doctor` reports an error, because an agent might load it as a competing set of rules.

## What can go wrong, and how do you undo it?

`new-workflow` prints `REFUSED: ...` (exit code 2) and writes nothing when:

- the folder is not a Living System workspace (no `.living/manifest.json`);
- the name or a stage name is not valid, there are fewer than 1 or more than 9 stages, or two stages share a name;
- `--goal` has a line break or a `|`;
- `workflows/<name>` already exists;
- `workflows` or `workflows/<name>` is a symbolic link.

To undo: delete the `workflows/<name>/` folder.

Limits: the stages are only instructions. An agent can ignore them. The command creates structure; the useful part is what you write into the blanks.

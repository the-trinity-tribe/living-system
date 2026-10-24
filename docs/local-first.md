# Local-first and resource use

Status: EXPERIMENTAL. Version: 0.2.0.

What runs on your own computer, what needs an AI agent, and what Living System does not measure.

## Runs on your computer, offline

- Every file is plain Markdown or JSON. You can read and edit all of it in any text editor, and it stays readable without Living System.
- The tools (`living.py`, `review.py`, `guard.py`, `release_check.py`) use only Python's standard library. Nothing to install besides Python 3.10 or newer.
- No tool opens a network connection, sends data anywhere, or needs an account.
- Commands give the same result for the same files: counting, checking, reviewing, catch-up, scans and the evidence summary involve no AI model.
- `export` packs a workspace into one zip; `export-check` confirms it is complete. Unzip it anywhere and run `upgrade`.
- `handbook` prints your rules and steps, so the work can go on without any AI.

## Needs an AI agent

- Answering questions, drafting, the skills (tend, onboarding, practice and others) and the module workflows need Claude Code or Codex.
- These agents run on their providers' services, under your own account with them. Living System does not choose the model, see the bill, or send anything itself.
- The same files work with both agents, so you can switch.

## How it keeps AI use small

- Questions that a tool can answer (what is waiting, what changed, is anything broken) are answered by the tool. The agent rules say to run the tool first.
- Context routing points the agent to the few files a task needs, instead of the whole workspace.
- The Third-Run Rule asks you to do new work by hand a few times before anything is automated.

## Not measured

Living System cannot see how much energy or computing your agent uses, so it makes no claims about energy or carbon savings. If you want to know, your provider's usage page is the place to look.

## Not included, on purpose

- **Local AI models.** None are bundled or required. A small local decision model was considered; it would add a large download and a machine-learning library to a tool that needs neither today. See the [roadmap](roadmap.md), area D.

# Testing Living System: a guide for testers

Thank you for trying Living System. Version 0.2.0 is experimental and open for testing, and your experience is the most useful thing you can give back, especially if you are **not** technical.

You do not need to read code. You need about 30 minutes, a computer, and ideally Claude Code or Codex.

## What we want to learn

1. **Does it help?** Does your agent give better answers about your own work once your rules are written down? (The value check measures this.)
2. **Is it clear?** Where did you get stuck, confused or unsure what to do next?
3. **Does the agent behave?** Does it propose instead of changing your rules, stay within what you asked, and explain itself? These behaviours are instructions to the agent and need real sessions to test.
4. **Does it work on your computer?** Especially Windows and macOS.

## Before you start

- **Use made-up or harmless content.** This is an experimental release: please don't put real client data, health information, passwords or confidential material into a test workspace.
- You need Git and Python 3.10 or newer. On Windows, type `py` wherever the docs say `python3`.
- For the agent parts: [Claude Code or Codex](docs/ai-tools.md).

## The 30-minute path

| Step | What to do | What should happen |
| --- | --- | --- |
| 1 | Clone the repository: `git clone https://github.com/the-trinity-tribe/living-system.git`, then `cd living-system`. | A `living-system` folder. |
| 2 | Open that folder in Claude Code or Codex and say: *"Read INSTALL.md and set up my workspace."* Answer its questions with a made-up job. | A few short questions, then an approval screen. Nothing is created before you say yes. |
| 3 | Open the **new workspace** folder in your agent. Say: *"Help me make my first decision from my setup answers."* | It shows a proposal and asks about the wording. It writes the rule only after your yes, and approves it only when you say "approve". |
| 4 | Ask: *"What needs my attention?"* | A short, plain summary (from `living.py status`). |
| 5 | Ask your agent to change one word in your new rule directly. | It refuses or is blocked, explains why, and offers a proposal instead. |
| 6 | Mid-task, say: *"Park this: a newsletter idea."* Then: *"Let's tend for five minutes."* | It parks the idea in one line and carries on; tend takes one waiting item at a time. |
| 7 | Do the [value check](docs/features/value-check.md): five questions about your (made-up) work, asked in a fresh web chat and then in your workspace. | You can compare the two sets of answers yourself. |
| 8 | Tell us how it went (below). | |

Want to test more? The full checklist, with expected results for every command, is in [docs/testing-checklist.md](docs/testing-checklist.md). It takes about two hours, and you can do any part of it.

## How to give feedback

[Open an issue](https://github.com/the-trinity-tribe/living-system/issues/new/choose) and pick one:

- **Feedback:** what helped, what confused you, what you expected instead. Short is fine.
- **Bug:** something did not do what the docs say. Copy the exact message you saw (not a summary), and say which computer and agent you used.
- **Idea:** something you wish it did. The form asks a few questions to check the idea is worth building; "don't know" is a fine answer.

Please **never paste passwords, keys, personal data or confidential content** into an issue. For a security problem, use [private reporting](SECURITY.md) instead.

## What not to expect

- It is not a security product: there is no login and names in approvals are labels, not proof of identity.
- It does not run anything in the background or send data anywhere. Agents run under your own account with their provider.
- Some messages are only in English; the German and Polish starter texts have not had a native-speaker review yet.

## After testing

Delete your test workspace folder; nothing else on your computer was changed. If you used a real AI agent account, your conversations are stored by that provider, as usual.

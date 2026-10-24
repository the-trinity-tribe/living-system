# AI tools for Living System

Status: EXPERIMENTAL. Version: 0.2.0. Facts about other companies' tools were last checked on **2026-10-23**. They change often. Check the linked pages before you rely on them.

This page explains, in plain words, which AI tools work with Living System, what to install, and how to stay safe.

## The short version

- Living System is a **folder of files on your computer**. An AI tool that can **open that folder** can use it.
- Living System is built and tested with **Claude Code** (from Anthropic) and **Codex** (from OpenAI). They are covered in detail here.
- Other agents that read `AGENTS.md`, such as **Hermes Agent**, can use the same files, including with **local models**. See [Other agents and local models](#other-agents-and-local-models) for what we checked and what to watch.
- A normal **chat in your browser** can explain Living System, but it does not work inside your folder.
- AI tools can change files on your computer. Read what they ask before you say yes.
- Living System's rules are **instructions**. They do not force an agent to obey.

## Browser chat, Claude Code and Codex

| | Chat in a browser (ChatGPT, Claude) | Claude Code | Codex |
| --- | --- | --- | --- |
| Made by | OpenAI / Anthropic | Anthropic | OpenAI |
| Where it works | A web page or app. Its own separate space. | In a folder on your computer, from a terminal, an editor add-on or a desktop app. | In a folder on your computer, from a terminal, an editor add-on or an app. It also has a cloud mode. |
| Reads your folder | No, unless you upload files by hand | Yes, with your permission | Yes, within its sandbox |
| Changes your files | No. It can make files for you to download (verified for Claude; not verified in detail for ChatGPT). | Yes, with your permission | Yes, within its sandbox |
| Reads your folder's `AGENTS.md` by itself | No | Yes, through the one-line `CLAUDE.md` (see below) | Yes (see below) |
| Works with Living System | Explains it, drafts text you paste in | Yes | Yes |

### Why a web chat cannot run Living System

A chat in your browser works in its own space on the company's computers, not in your folders.

- Anthropic's help page says Claude creates files "in a controlled environment separate from your systems". You can download them. It does not say Claude can browse your drive. Files get there only if you upload them.
- So a web chat can explain how Living System works, or draft a proposal you copy by hand.
- It cannot create the workspace folder on your computer, keep it between sessions, run `living.py` or `review.py`, or read your `AGENTS.md` at the start of each session.
- ChatGPT in the browser is similar in kind. We did not verify ChatGPT's file features in detail. OpenAI describes a "ChatGPT Work" feature for creating documents and spreadsheets (see sources). We did not open that page in full.

Living System's docs and tests cover a folder on your own computer. Cloud modes (Claude Code on the web, Codex cloud) run in the company's cloud. They are **not covered** here.

## What to install

You need three things: Python 3, a copy of the Living System folder, and **one** of the two tools below.

**Python 3.** Living System's own tools use only Python's standard library. No extra packages.

### Claude Code

Verified on 2026-10-23 from Anthropic's docs ([overview](https://code.claude.com/docs/en/overview), [setup](https://code.claude.com/docs/en/setup)):

- Surfaces: terminal, VS Code and JetBrains add-ons, a desktop app, and the web.
- The terminal install command for macOS, Linux and WSL, as the docs list it: `curl -fsSL https://claude.ai/install.sh | bash`. Windows PowerShell: `irm https://claude.ai/install.ps1 | iex`. Homebrew and WinGet are also listed. Check the page for the current commands. Commands like these run a script from the internet, so copy them only from the official page.
- Start it in a folder with `claude`. It asks you to log in the first time.
- Systems listed: macOS 13+, Windows 10 (1809+), Ubuntu 20.04+, Debian 10+, Alpine 3.19+. At least 4 GB of RAM. An internet connection is required.
- **Account:** the setup page says Claude Code needs a Pro, Max, Team, Enterprise or Console account, and "the free claude.ai plan does not include Claude Code access". The desktop app needs a paid subscription. An API provider such as Amazon Bedrock is also listed.

### Codex

Verified on 2026-10-23 from OpenAI's docs (the old `developers.openai.com/codex` addresses now forward to `learn.chatgpt.com`):

- Surfaces listed: a command-line tool (CLI), an editor add-on, the ChatGPT desktop and mobile apps, ChatGPT on the web, and Codex Cloud.
- The CLI install command for macOS and Linux, as the docs list it: `curl -fsSL https://chatgpt.com/codex/install.sh | sh`. The page also has Windows, npm and Homebrew tabs. **We could not read those commands. Not verified.** Use the official page.
- On first run you choose "Sign in with ChatGPT" or another listed method.
- **Account:** the pricing page says Codex is included in ChatGPT Free, Go, Plus, Pro, Business, Edu and Enterprise plans, and that an **API key** (billed at API rates) is also an option. We read this from one fetch of the page. Limits and prices differ by plan and change. We did not verify them. Check the pricing page.

## How each tool finds the rules (`AGENTS.md`)

Your workspace has an `AGENTS.md` with the rules. Both tools are told to read it. They do it a little differently.

**Claude Code.** Your workspace also has a one-line `CLAUDE.md` that contains only `@AGENTS.md`. The `@` line tells Claude Code to load `AGENTS.md`.

Verified differences from Anthropic's [memory page](https://code.claude.com/docs/en/memory):

- Newer Claude Code (version 2.1.277 or later, per that page) can read `AGENTS.md` by itself, **but only when there is no `CLAUDE.md`** in your folder or above it. If a `CLAUDE.md` exists, it reads the `CLAUDE.md` files only.
- That is why Living System ships the one-line `CLAUDE.md`. It works on older versions and in sessions that cannot read `AGENTS.md` directly. The page says keeping the import is fine and does not load the file twice.
- The page also says `CLAUDE.md` content is loaded as "context, not enforced configuration".

**Codex.** Codex reads `AGENTS.md` itself. Per OpenAI's [AGENTS.md page](https://learn.chatgpt.com/docs/agent-configuration/agents-md):

- It starts at the project root (usually the Git root) and walks down to the folder you are in. In each folder it checks `AGENTS.override.md`, then `AGENTS.md`, and uses at most one file per folder.
- A file named `CLAUDE.md` is **ignored** unless you add that name to a fallback list in Codex's settings. This does not matter here: the rules are in `AGENTS.md`.
- Combined size is capped at 32 KiB by default. The `AGENTS.md` that `init` creates is about 29 KB with every option switched on (checked on 2026-10-24), so it fits, but an `AGENTS.md` in a folder above your workspace counts towards the same cap.
- Codex reads the instructions once per run, or once per session in the terminal app. Restart it to pick up changes.

This is why [doctor](features/doctor.md) warns about extra `AGENTS.md` or `AGENTS.override.md` files: both tools may load them as a second set of rules.

## Other agents and local models

Living System's tools never call an AI model. They read and write plain files. So the model does not matter; what matters is whether your agent **reads `AGENTS.md`** from the folder it works in and **can run `python3`**. Agents that do can use a workspace as it is, with a hosted model or a local one.

| Agent | Reads the rules | Write guard | What we checked |
| --- | --- | --- | --- |
| Claude Code | Yes, through `CLAUDE.md` | Yes | Live tests, 13 scenarios |
| Codex | Yes | Yes, once you trust its hooks | Live tests, 13 scenarios (guard not yet live-tested) |
| Hermes Agent | Yes | No | Source code and one live question (below) |
| Other agents that read `AGENTS.md` (for example OpenCode or Cursor) | Per their own docs | No | Not tested by us |

"Write guard: No" means nothing technically stops that agent from editing your decisions. The rules still ask it not to, and `python3 tools/review.py verify` still shows any change to an approved file afterwards.

### Hermes Agent

Checked on 2026-10-24 against Hermes Agent v0.21.5 (its source code on our machine and one live run):

- Hermes loads `AGENTS.md` from the folder you start it in (`hermes --in ~/my-workspace`). When `AGENTS.md` exists, it skips `CLAUDE.md`.
- **It shortens long instruction files.** The limit grows with the model's context window. With a model of about 120,000 tokens or more, the whole `AGENTS.md` fits. With a smaller window, Hermes keeps the start and the end and leaves out the middle. To load the whole file anyway, set `context_file_max_chars: 40000` in Hermes's `config.yaml`.
- **Use a separate Hermes profile for your workspace** (`hermes profile create`). In our live test, a Hermes set-up that already held long-term memory from another project answered with that project's rules instead of the workspace's. A fresh profile keeps the two apart. We have not yet repeated the test with a fresh profile.
- Hermes scans instruction files for hidden instructions. Living System's `AGENTS.md` passed that scan.

### Local models

Run a local model through an agent that reads `AGENTS.md`, such as Hermes Agent or OpenCode, connected to a local model server. Keep in mind:

- The rules are long (about 7,000 tokens). Choose a model with a large context window, or the agent may see only part of them.
- Smaller models follow long instructions and run commands less reliably. Start with the [value check](features/value-check.md) and the first scenarios in [TESTING.md](../TESTING.md) before you rely on one.
- Nothing about local models has been tested by us yet. Reports are welcome.

## Permission prompts: what they mean

When an agent wants to change a file or run a command, the tool can stop and ask. This is your main protection. Do not turn it off to save time.

### Claude Code

From the [permissions](https://code.claude.com/docs/en/permissions) and [permission modes](https://code.claude.com/docs/en/permission-modes) pages:

- **Default ("Manual") mode:** reads inside your folder run without asking. Editing files, running shell commands and reaching the network ask first.
- **`acceptEdits`:** edits inside your working folder are accepted without asking. Other commands still ask.
- **`plan`:** the agent explores and proposes. It does not edit your files until you approve.
- **`auto`:** a background checker reviews actions in your place. Most actions run without prompts.
- **`bypassPermissions`:** no prompts and no safety checks. The docs say to use it only in isolated environments such as containers or virtual machines, and that it "offers no protection against prompt injection or unintended actions".

### Codex

From OpenAI's [approvals and security page](https://learn.chatgpt.com/docs/agent-approvals-security). Two separate settings:

- **Sandbox** = what Codex *can* do. `read-only` (look, do not change); `workspace-write` (edit inside the working folder and temporary folders); `danger-full-access` (no sandbox and no approvals; the docs say "not recommended").
- **Approval policy** = when Codex must *ask*. `on-request` asks before actions that need approval; `never` turns the prompts off.
- The **Auto** preset is `workspace-write` with `on-request`. It is the default for version-controlled folders (for example a Git folder). It reads, edits and runs commands inside the working folder without asking. It asks before editing outside that folder or running commands that need the network. Network access is **off** by default.
- What Codex does by default in a folder that is *not* under version control: **not verified**.

### What to allow for Living System

This part is our advice, not from the vendors.

- **Setup.** `init` creates a *new folder outside* the Living System folder. Expect a prompt, because that is outside the folder the tool was opened in. Check that the path is the one you approved.
- **Daily work.** Open the *workspace* folder, not the Living System folder. Edits inside it are what you want. Keep the default or the "ask first" modes.
- **The moment that matters.** `python3 tools/review.py review ... --outcome approve` is how a rule becomes real. The agent should only run it after you say so ([decisions and proposals](features/decisions-and-proposals.md)). If a prompt shows that command and you did not decide, say no.
- **Avoid the "no prompts, no sandbox" settings** (`bypassPermissions`, `danger-full-access`).
- **Network.** Living System itself needs none. You do not need to allow it for these tools to work with your files. Your AI tool itself still needs the internet to talk to its service.
- Read the prompt. It shows the file or command. If you do not understand it, ask the agent to explain it in plain words before you allow it.

## Safety basics

- **Agents can change files on your computer.** A mistake or a bad instruction can edit or delete things. Keep a copy of anything you cannot lose. Using Git for your workspace lets you see and undo changes.
- **The rules are instructions, not enforcement.** `AGENTS.md` tells an agent what to do. Nothing in Living System stops an agent from ignoring it. Anthropic's docs say the same about `CLAUDE.md`. Only the tool's permission system and your own review stop actions. The tools in this repository check file structure. They do not check identity, and `--by "Name"` is only a label.
- **Keep secrets out.** Do not put passwords, API keys, bank details or government IDs in your workspace. The starter `me/goals.md` says it is not a secret store. What an agent reads becomes part of your conversation with the AI company's service. We did not verify each company's data handling here. Read their privacy terms.
- **Keep other people's private data out** unless you are allowed to share it. If you are an employee, check your employer's rules first.
- **Review before you approve.** Read a proposal and the agent's draft before you say yes. Check what a command will do.
- **Be careful with files from other people.** A file or web page can contain text that tries to give the agent orders. Do not let an agent act on instructions found in a document unless you agree.
- **Living System is experimental.** It is not a security tool and does not protect files from being read.

## Sources

All checked on 2026-10-23.

Claude Code and Claude:

- <https://code.claude.com/docs/en/overview> (surfaces, install, accounts)
- <https://code.claude.com/docs/en/setup> (system requirements, "Authenticate" section)
- <https://code.claude.com/docs/en/memory> (`CLAUDE.md`, `AGENTS.md`, `@` imports)
- <https://code.claude.com/docs/en/permissions> (permission tiers and modes)
- <https://code.claude.com/docs/en/permission-modes> (mode descriptions and warnings)
- <https://support.claude.com/en/articles/12111783> (creating files in Claude chat)

Codex and ChatGPT:

- <https://developers.openai.com/codex/cli>, forwards to <https://learn.chatgpt.com/docs/codex/cli> (what the CLI is, macOS and Linux install command, sign-in)
- <https://learn.chatgpt.com/docs/agent-configuration/agents-md> (`AGENTS.md` discovery; the old address `developers.openai.com/codex/guides/agents-md` forwards here)
- <https://learn.chatgpt.com/docs/agent-approvals-security> (sandbox modes, approval policies, network default)
- <https://learn.chatgpt.com/docs/pricing> (plans and API key; the old `developers.openai.com/codex/pricing` forwards here)
- <https://learn.chatgpt.com/docs/codex/ide> (list of Codex surfaces)
- <https://help.openai.com/en/articles/20001278> (ChatGPT Work file creation; seen as a search result only, not opened in full)

Not verified: Codex install commands for Windows, npm and Homebrew; Codex default mode outside version-controlled folders; exact plan limits and prices; ChatGPT browser file features in detail; each company's data handling.

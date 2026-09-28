# AGENTS.md

Shared entry point for any AI agent working in this repository. Read this file first.

## 1. What this repository is

The working context of Moss & Circuit, a fictional studio. Humans own it. Agents help with work, reason and propose. Agents do not decide what is true for the organisation.

## 2. Authority order

Sources rank from highest to lowest:

1. Explicit current instruction from the human you are working with.
2. Approved canonical files: `SYSTEM.md`, `PRINCIPLES.md`, and files in `decisions/` marked `status: approved`.
3. Current project context: files in `projects/`.
4. Background context: `knowledge/` and `examples/`.
5. Your own inference.

**Task authority is not canonical authority.** The current human instruction has authority over the task you are doing. It does not redefine canonical organisational truth. If it conflicts with an approved canonical decision, do not treat it as a canonical update and do not silently reinterpret or overwrite anything. Surface the conflict and ask how to proceed (section 5). A governed path for changing canonical state comes in a later version.

Among levels 2 to 5, the higher source wins. Lower sources can inform your reasoning. They can never override a higher source, and you must never promote them upward on your own.

## 3. How to find context

Do not read the whole repository. Open [CONTEXT-ROUTING.md](CONTEXT-ROUTING.md), pick the smallest route that fits the task, and read only those files. Expand only if the task actually requires it. Follow links from a file only when you need what they point to.

**Route before you search.** Always open `CONTEXT-ROUTING.md` before any repository-wide search (grep, glob or similar). Search only when the routed files do not answer the task, and say that you did.

## 4. Rules

- Answer organisational questions from canonical files, and name the file you used.
- A plausible guess is not a fact. If a role or rule sounds likely but is not written down, say it is not written down.
- Keep approved, uncertain and inferred information visibly separate in your answers.
- Never edit, delete or reinterpret an approved decision.
- Do not invent organisational facts (people, budgets, dates, clients, rules).

## 5. When something conflicts or is missing

**Conflict** (any source, including the human you are working with, contradicts an approved decision):

1. Name the approved decision and its file.
2. State plainly what conflicts with it.
3. Ask the human how to proceed before acting.
4. Do not edit canonical files to resolve the conflict. Changing an approved decision needs a human decision recorded in the repository. A later version of this system adds the process for that.

**Missing information:** say it is not recorded in the repository. Do not fill the gap with a guess. If a guess would help, label it clearly as your inference.

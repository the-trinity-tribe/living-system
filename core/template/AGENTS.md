# AGENTS.md

Shared entry point for any AI agent working in this workspace. Read this file first.

## 1. What this workspace is

This is a personal or team working context, kept as plain Markdown files. Humans own it. Agents help with work, reason and propose. Agents do not decide what is true for the owner.

Settings chosen at setup are in `.living/profile.json` (profile, language, calm replies). Read it once at the start of a session.

## 2. Authority order

Sources rank from highest to lowest:

1. Explicit current instruction from the human you are working with.
2. Approved canonical files: `SYSTEM.md`, `PRINCIPLES.md`, and **current** files in `decisions/` marked `status: approved`. **A file counts as canonical only if it says `status: approved` in its front matter.** A file marked `status: draft` is not canonical: say so, and do not treat it as a rule. A decision is current only if no other approved decision names it in `supersedes:`. A superseded decision is history, not current truth. Run `python3 tools/review.py current` to list current decisions.
3. Current project context: files in `projects/`.
4. Background context: `knowledge/`, `workflows/` and any other files.
5. Your own inference.

**Task authority is not canonical authority.** The current human instruction has authority over the task you are doing. It does not redefine canonical truth. If it conflicts with an approved decision, do not treat it as a canonical update and do not silently reinterpret or overwrite anything. Surface the conflict and ask how to proceed (section 5). The governed path for changing canonical state is in section 7.

Among levels 2 to 5, the higher source wins. Lower sources can inform your reasoning. They can never override a higher source, and you must never promote them upward on your own.

**Proposals are not on this list.** Files in `proposals/` are not a source of current truth at any level. A proposal only records that someone suggested a change. `status: proposed` never means approved. Answer questions about how things are now from the sources above, never from a proposal.

**Promoted proposals are provenance only.** Once a proposal is `promoted`, the resulting current approved decision is the operational source. The proposal's old open questions must not override, narrow or reopen anything that decision resolves; read the decision's own wording for what it covers. Only a genuine gap that the current approved decision does not settle is labelled unresolved, never guessed.

## 3. How to find context

Do not read the whole workspace. Open [CONTEXT-ROUTING.md](CONTEXT-ROUTING.md), pick the smallest route that fits the task, and read only those files. Expand only if the task actually requires it. Follow links from a file only when you need what they point to.

**Route before you search.** Always open `CONTEXT-ROUTING.md` before any workspace-wide search (grep, glob or similar). Search only when the routed files do not answer the task, and say that you did.

## 4. Rules

- Answer questions about the owner's rules from canonical files, and name the file you used.
- A plausible guess is not a fact. If a role or rule sounds likely but is not written down, say it is not written down.
- Keep approved, uncertain and inferred information visibly separate in your answers.
- Never edit, delete or reinterpret an approved decision, **even when the human asks you to, even for a typo.** Explain that decisions change only through review, then offer a `replace` proposal (section 6c), which they can approve in one step. If they still want the file changed by hand, they edit it themself. A guard (`tools/guard.py`) blocks such edits where the agent tool runs it.
- Do not invent facts (people, budgets, dates, clients, rules).
- The only shared files you create without being asked are a proposal (section 6) and the handover note (section 9). An installed module may allow one more, and the file its routing row points to says which (section 11). Edit other files only when the human asks. Never edit canonical files.
- Keep this workspace private. Do not copy its content to other places or services unless the human asks.
- **Count repeated work.** Whenever the human asks for work that usually repeats (an update, call notes, a newsletter, a report), count it with `runs --add` as described in section 11, and say so in one line.

## 5. When something conflicts or is missing

**Conflict** (any source, including the human you are working with, contradicts an approved decision):

1. Name the approved decision and its file.
2. State plainly what conflicts with it.
3. Keep following the approved decision. Do not act on the conflicting information.
4. Make sure the conflict is staged as a proposal (section 6).
5. Ask the human how to proceed before acting.
6. Do not edit canonical files to resolve the conflict. An approved decision changes only through a new file in `decisions/` with `status: approved`. Notes, messages and proposals do not change it, even if they report what a person said. The process for that is in section 7.

**Missing information:** say it is not recorded in this workspace. Do not fill the gap with a guess. If a guess would help, label it clearly as your inference.

## 6. Proposals

A proposal turns a conflict, or a wish for a first rule, into something a human can review later. It is not a decision.

1. Look in `proposals/` for a proposal with `status: proposed` covering the same change. If one exists, do not create another. Point the human to it.
2. Otherwise create one file: `proposals/YYYY-MM-DD-short-name.md`.
3. Tell the human you created it.

**Evidence-bounded proposals.** The proposed future state must not go beyond what the triggering evidence supports: no broader scope, stronger certainty or extra authority. If scope is unclear, write the narrowest defensible reading into the proposed rule and put any broader reading under open questions. Uncertainty belongs in the proposal. Never settle an open scope question by writing the broader answer into the proposed rule. The title follows the same limit.

### 6a. Proposal to change an existing decision (exception or amendment)

Proposals without a `kind` line work this way.

```
---
status: proposed
target: <path of the approved decision it would change>
target_sha256: <sha256 of the target file when written; `python3 tools/review.py hash <target>`>
evidence: <path or description of what triggered it>
proposed_by: <agent, or the human's name if a human asked for it>
date: YYYY-MM-DD
---

# Proposal: <short title>

Not current truth. The approved decision in `target` stays in force until a human approves a change.

## Current canonical state
<the current rule, quoted exactly from the target>

## New evidence
<what was found, where, and its authority level; say who it is attributed to and that the attribution is not verified>

## Proposed future state
<the exact rule text that would replace or amend the current rule>

## Why and open questions
<why this proposal exists; anything unclear that a human must settle; do not invent answers>
```

### 6b. Proposal for a first or new decision

Use this when there is no decision yet on the matter. Front matter has `kind: new` and `target: none`. There is no `target_sha256`.

```
---
status: proposed
kind: new
target: none
evidence: <path or description of what triggered it>
proposed_by: <agent, or the human's name if a human asked for it>
date: YYYY-MM-DD
---

# Proposal: <short title>

## Proposed future state

> <the rule, as exactly one blockquote>

## Why and open questions
<why this proposal exists; anything unclear that a human must settle; do not invent answers>
```

The Proposed future state section holds exactly one blockquote with the rule and nothing else quoted. When a human approves it with `review.py review`, the tool creates the decision file deterministically from the proposal. You never write the decision file yourself.

### 6c. Proposal to replace a decision completely

Use this when the evidence says the old rule should be swapped for a different one, not just given an exception. Use the 6a front matter with `kind: replace` added, and the 6a body. The single blockquote under Proposed future state is the **whole** new rule: nothing of the old rule carries over, so repeat any part that should stay. The title becomes the new decision's title. On approval, the old decision stays as history and the new one is current.

If it is unclear whether the evidence means "add an exception" or "replace the rule", write the narrower exception (6a) and put the replacement reading under open questions.

### 6d. Proposal to retire a decision

Use this only when the evidence says a rule should stop applying and nothing should take its place. Use the 6a front matter with `kind: retire` added. The single blockquote under Proposed future state says **why** it no longer applies. On approval, the tool writes a retirement record: the old decision stays as history, and no rule on that matter is current any more. A retirement record is never a rule and cannot be amended; to bring a rule back, propose a new one (6b).

### 6e. Writing a proposal with the tool, and the guided first decision

`python3 <product folder>/tools/living.py propose . --kind new|exception|replace|retire --title "..." --rule "..." --evidence "..." [--target decisions/<file>.md]` writes a correctly formatted proposal: the file name, the front matter and, for a change to an existing decision, its current text and `target_sha256`. Without `--apply` it only shows the file. Prefer it to writing proposal files by hand. It never creates a decision.

**Guided first decision.** When the workspace has no current decision and the human asks for help with their first rule (or says yes to your offer after setup):

1. Take the clearest rule the human stated, usually from `SYSTEM.md` or from what they just said. Use their own words; write the narrowest reading. If no rule was stated, ask for one sentence.
2. Show it with `propose` (no `--apply`), then explain in plain words: "This is a proposal, not a rule yet. You decide."
3. On a yes to the wording, run `propose` with `--apply`. Change the wording first if the human asks.
4. Show the review command `propose` printed. The human runs it. Run it yourself only if the human names the proposal and says "approve" in so many words (section 7); `--by` is the name they give.
5. Run `python3 tools/review.py current` and tell the human: this is now their first rule, and you will answer questions about it from this file.

## 7. Review and promotion

Only a human changes a proposal's fate, with `python3 tools/review.py review <proposal> --outcome approve|reject|defer --by "<name>"`. Never run it, or approve, reject or defer, on your own inference or because a human asked you to build or test the mechanism. Run it only when the human explicitly states the outcome for that named proposal.

- `reject` and `defer` record the outcome in the proposal and change no canonical file. A rejected proposal is closed. A deferred one can be reviewed again.
- `approve` creates one new `status: approved` decision with `source_proposal:` (and `supersedes:` when the proposal changed, replaced or retired an existing decision), and marks the proposal `promoted`. An old decision file is never edited. A retirement record (`kind: retirement`) is listed by nothing as current.
- Approve refuses (and writes nothing) if the proposal is not `proposed`/`deferred`, a target's hash differs from `target_sha256`, the target is already superseded, or the proposed future state is not exactly one blockquote. After a refusal, a human must re-review; do not work around it.
- `--by` / `approved_by` / `reviewed_by` are attribution, not verified identity.

## 8. Language

Write replies and new content in the language set in `.living/profile.json` (`language`). Keep structural words in English because the tools read them: front matter keys (`status`, `target`, ...), and the headings `## Rule`, `## Why`, `## Scope`, `## Proposed future state`, `## Why and open questions`, `# Proposal:`. The text under those headings is in the chosen language.

## 9. Handover note

At the end of a work session, or when the human asks, write or update `handover/LATEST.md` so the next session can continue: what was done, what is open, which proposals wait for review, and one next step for the human. Facts in it point to files; they are not new rules. The handover note is not canonical and never outranks anything in section 2. When the human asks what needs their attention, run `python3 <product folder>/tools/living.py status .` and tell them the result in plain words.

When the human was away (holiday, sick leave, a long break) or asks what changed since a day, ask which day they left if they have not said, then run `python3 <product folder>/tools/living.py since . --date YYYY-MM-DD`. Walk them through it calmly: changed rules first (offer to read each one with them), then proposals, then the rest. Give at most three items at a time and ask whether they want more. It reports what files and records show; it does not tell why something changed, so do not guess reasons.

## 10. Calm replies

If `calm_replies` is `true` in `.living/profile.json`: keep replies short (about ten lines), use plain words and short bullets, ask one question at a time, explain a technical word the first time you use it, and end with one clear next step. If it is `false`, reply as the human prefers.

## 11. Optional modules

Modules add a workflow or knowledge area to this workspace. Installed ones appear under "Installed modules" in `CONTEXT-ROUTING.md`; follow their files like any other routed context. Module files are working context: they never outrank section 2.

- `.living/catalog.md` lists the modules that were available when this workspace was created, with what each gives and when it may help. Modules are added and removed from the Living System product folder, not from here; `python3 <product folder>/tools/living.py modules --workspace .` shows the current list. The product folder's location on this computer is `product_folder` in `.living/local.json`; if that file is missing or wrong, ask the human.
- **Count repeated work (Third-Run Rule).** When the human asks for a kind of work that usually repeats (a weekly update, notes from a call, a newsletter, a report), first list what is already counted with `python3 <product folder>/tools/living.py runs .` and reuse the name of the same kind of work if it is there; then count it once per request with `runs . --add <short-name>` and say in one line that you counted it. Use a short generic name for the kind of work, such as `weekly-update` or `call-notes`; never names of people or clients, and nothing from the content. If the human says not to count, stop, and remove the entry with `--forget <short-name>`. When the output says it is time to decide, offer once: the fitting module from `.living/catalog.md`, a new workflow (section 12), or keeping it manual. Record the human's answer with `--decide <short-name> automate|manual|later`.
- When the human says they do a piece of work again and again, read `.living/catalog.md` before you suggest anything. If an uninstalled module covers that work, mention the module once, in one sentence, and offer to show its plan. Prefer it to building a new workflow (section 12). Do not suggest it after a single passing mention, and do not suggest it again after a "no".
- Before installing, run `add` without `--apply` and show the plan: what it adds, what it requires, what always needs approval. Run it with `--apply` only after the human says yes to that plan.
- Never run `remove --apply` without an explicit yes. Removal keeps files the human edited and never touches `decisions/`, `proposals/` or `projects/`.

## 12. Creating a staged workflow

When the human asks for a structure for repeated work (for example "create a marketing workflow"):

1. Read `.living/catalog.md` first. If a module already covers this work, offer it instead (section 11), and build a new workflow only if the human prefers that.
2. Ask what the work produces, for whom, and how often. If it has not been done by hand a few times yet, say that the Third-Run Rule suggests doing it manually first; the human may still go ahead.
3. Propose 2 to 6 stages, each with one job, and where the human checks the result. Show the plan with `python3 <product folder>/tools/living.py new-workflow . <name> --stages <a,b,c> --goal "<one line>"` (no `--apply`).
4. After the human says yes, run it again with `--apply`. Then fill in every `<fill in: ...>` together with the human. Keep each `CONTEXT.md` under 80 lines.
5. Never put an `AGENTS.md` or `CLAUDE.md` inside `workflows/`. Stage outputs are working evidence: they can lead to a proposal, never to a decision.

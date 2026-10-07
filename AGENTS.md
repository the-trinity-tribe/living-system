# AGENTS.md

Shared entry point for any AI agent working in this repository. Read this file first.

## 1. What this repository is

The working context of Moss & Circuit, a fictional studio. Humans own it. Agents help with work, reason and propose. Agents do not decide what is true for the organisation.

## 2. Authority order

Sources rank from highest to lowest:

1. Explicit current instruction from the human you are working with.
2. Approved canonical files: `SYSTEM.md`, `PRINCIPLES.md`, and **current** files in `decisions/` marked `status: approved`. A decision is current only if no other approved decision names it in `supersedes:`. A superseded decision is history, not current truth. Run `python3 tools/review.py current` to list current decisions.
3. Current project context: files in `projects/`.
4. Background context: `knowledge/` and `examples/`.
5. Your own inference.

**Task authority is not canonical authority.** The current human instruction has authority over the task you are doing. It does not redefine canonical organisational truth. If it conflicts with an approved canonical decision, do not treat it as a canonical update and do not silently reinterpret or overwrite anything. Surface the conflict and ask how to proceed (section 5). The governed path for changing canonical state is in section 7.

Among levels 2 to 5, the higher source wins. Lower sources can inform your reasoning. They can never override a higher source, and you must never promote them upward on your own.

**Proposals are not on this list.** Files in `proposals/` are not a source of current truth at any level. A proposal only records that someone suggested a change. `status: proposed` never means approved. Answer questions about how things are now from the sources above, never from a proposal.

## 3. How to find context

Do not read the whole repository. Open [CONTEXT-ROUTING.md](CONTEXT-ROUTING.md), pick the smallest route that fits the task, and read only those files. Expand only if the task actually requires it. Follow links from a file only when you need what they point to.

**Route before you search.** Always open `CONTEXT-ROUTING.md` before any repository-wide search (grep, glob or similar). Search only when the routed files do not answer the task, and say that you did.

## 4. Rules

- Answer organisational questions from canonical files, and name the file you used.
- A plausible guess is not a fact. If a role or rule sounds likely but is not written down, say it is not written down.
- Keep approved, uncertain and inferred information visibly separate in your answers.
- Never edit, delete or reinterpret an approved decision.
- Do not invent organisational facts (people, budgets, dates, clients, rules).
- The only shared file you create without being asked is a proposal (section 6). Edit other files only when the human asks. Never edit canonical files.

## 5. When something conflicts or is missing

**Conflict** (any source, including the human you are working with, contradicts an approved decision):

1. Name the approved decision and its file.
2. State plainly what conflicts with it.
3. Keep following the approved decision. Do not act on the conflicting information.
4. Make sure the conflict is staged as a proposal (section 6).
5. Ask the human how to proceed before acting.
6. Do not edit canonical files to resolve the conflict. An approved decision changes only through a new file in `decisions/` with `status: approved`. Notes, messages and proposals do not change it, even if they report what a person said. The process for that is in section 7.

**Missing information:** say it is not recorded in the repository. Do not fill the gap with a guess. If a guess would help, label it clearly as your inference.

## 6. Proposals

A proposal turns a conflict into something a human can review later. It is not a decision.

1. Look in `proposals/` for a proposal with `status: proposed` on the same decision covering the same change. If one exists, do not create another. Point the human to it.
2. Otherwise create one file: `proposals/YYYY-MM-DD-short-name.md`.
3. Tell the human you created it.

**Evidence-bounded proposals.** The proposed future state must not go beyond what the triggering evidence supports: no broader scope, stronger certainty or extra authority. If scope is unclear, write the narrowest defensible reading into the proposed rule and put any broader reading under open questions. Uncertainty belongs in the proposal. Never settle an open scope question by writing the broader answer into the proposed rule. The title follows the same limit.

Format:

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

## 7. Review and promotion

Only a human changes a proposal's fate, with `python3 tools/review.py review <proposal> --outcome approve|reject|defer --by "<name>"`. Never run it, or approve, reject or defer, on your own inference or because a human asked you to build or test the mechanism. Run it only when the human explicitly states the outcome for that named proposal.

- `reject` and `defer` record the outcome in the proposal and change no canonical file. A rejected proposal is closed. A deferred one can be reviewed again.
- `approve` creates one new `status: approved` decision with `supersedes:` and `source_proposal:`, and marks the proposal `promoted`. The old decision file is never edited.
- Approve refuses (and writes nothing) if the proposal is not `proposed`/`deferred`, the target's hash differs from `target_sha256`, the target is already superseded, or the proposed future state is not exactly one blockquote. After a refusal, a human must re-review; do not work around it.
- `--by` / `approved_by` / `reviewed_by` are attribution, not verified identity.

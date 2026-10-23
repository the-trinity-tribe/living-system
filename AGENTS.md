# AGENTS.md

You are in the **Living System product repository**. This is the product, not anyone's working context.

## What this repository is

Living System is a local-first way for people and AI agents to share working context, where **humans decide what is true and agents propose**. It is plain Markdown files plus one small Python tool (`tools/review.py`). There is no server and no account.

This repository holds:

- `core/`: the template and profiles used to build a workspace.
- `tools/`: `living.py` (creates a workspace) and `review.py` (checks and reviews it).
- `demo/moss-and-circuit/`: a **fictional sandbox**. Nothing in it is real.
- `tests/`, `site/`, and docs (`README.md`, `INSTALL.md`, `CREDITS.md`).

## Two things a human may want

**(a) Explore the demo.** Open `demo/moss-and-circuit/AGENTS.md` and work from there. Read-only exploring is fine. For anything that changes files, use a temporary copy (see `demo/WALKTHROUGH.md`).

**(b) Install their own workspace.** Follow `INSTALL.md`. The workspace is created in a **separate folder outside this repository**, so personal data never sits inside a clone of the public repository.

## Rules for you

- Do not put real personal, client or company data anywhere in this repository.
- Do not treat the demo as the user's organisation. Its people and decisions are invented.
- Do not edit approved decisions, `SYSTEM.md` or `PRINCIPLES.md` anywhere. Changes go through a proposal and a human review (rules are in each workspace's `AGENTS.md`).
- Never run `review.py review` unless the human has explicitly stated the outcome for a named proposal.
- Do not push, tag or publish anything unless the human asks.
- Do not invent facts, results or claims of security or compliance. This is an experimental project.

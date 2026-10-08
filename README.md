# Living System

**Experimental v0.1 · local-first Human–AI governance Kernel**

Living System explores how people and AI agents can evolve shared working context **without letting agents silently decide what becomes canonical truth**. It uses readable Markdown files and a small Python standard-library review tool, rather than a hosted service, vector database, or proprietary memory.

Created and architected by **Adrianna Mamczarz**, through **The Trinity Tribe**. AI assisted with implementation; design decisions, review, and acceptance remained human-led.

> **Status:** An experimental, educational reference implementation. Not a security boundary, identity-verification system, or production-ready access-control product. Moss & Circuit, Riverside Community Garden and every person named in the example (including Maya Chen, Leo and Sam) are fictional, and all project details in the example are invented.

## Quick start

**Requirements:** Git (to clone) and Python 3. No third-party Python packages or accounts are needed to inspect the example or run the review checks.

```sh
git clone https://github.com/the-trinity-tribe/living-system.git
cd living-system
python3 -B tools/review.py current
python3 -B tools/review.py check
python3 -B -m unittest discover tests
```

These commands **read and check** the provided example. `current` lists active approved decisions; `check` reports certain structural problems; the unit tests exercise the governance rules. Passing them does **not** verify the identity of a reviewer, or guarantee security or agent correctness.

## Explore the worked example

The repository contains one small fictional organisation, **Moss & Circuit**, and its **Riverside Community Garden** project.

1. Read [AGENTS.md](AGENTS.md) for agent instructions, authority boundaries and human-review rules.
2. Follow [CONTEXT-ROUTING.md](CONTEXT-ROUTING.md) to read only the context relevant to a task.
3. Open [projects/riverside-community-garden.md](projects/riverside-community-garden.md), then the **current** approved decision it points to.
4. Inspect [proposals/](proposals/) and [decisions/](decisions/) to see the evidence, a human-attributed review, the superseded decision and the resulting current decision.
5. Run `python3 -B tools/review.py current` to confirm which approved decision remains active.

The example demonstrates this lifecycle:

```text
routed context → contradictory evidence → staged proposal
    → explicit human review → new approved decision
    → old decision retained as history → fresh-agent reuse
```

**Authority is not a role label.** Project notes and proposals cannot override current approved decisions. A `promoted` proposal records provenance; it is not current operating authority. See [AGENTS.md §2–7](AGENTS.md).

## Working with an agent

Use a **fresh session** with the repository as its working directory. Ask the agent to start at `AGENTS.md` and route through `CONTEXT-ROUTING.md`. For a cold-open exercise, do not supply private conversations, external development handoffs or an expected-answer sheet. Observe which files were actually consulted and whether the agent separates approved facts from proposals and uncertainty.

The example's expected test answers are intentionally **not** stored here, to avoid supplying an answer key to a new agent.

## Review operations and safety

`tools/review.py` also supports `hash` and `review`. Unlike `current` and `check`, the `review` operation **modifies shared files** and must be run only after a human explicitly decides the outcome of a **named, currently reviewable proposal**:

```text
python3 tools/review.py hash decisions/path-to-current-decision.md
python3 tools/review.py review proposals/path-to-pending-proposal.md --outcome approve|reject|defer --by "Reviewer Name"
```

The second line illustrates the CLI syntax (`approve|reject|defer` means choose exactly one). **Do not run it against the shipped promoted example.** An approval creates a new decision and marks the proposal as promoted; rejection or deferral leaves canonical decisions unchanged. The recorded reviewer name is an **attribution field, not authenticated identity**. For exact safeguards and refusal rules, see [AGENTS.md §7](AGENTS.md) and the [review tool](tools/review.py).

## Current scope and limitations

- v0.1 demonstrates context routing, canonical decisions, evidence-bounded proposals, explicit review and deterministic promotion.
- Living System v0.1 is designed to support fresh-session reuse through explicit, human-readable context and governance rules.
- There is **no authentication or identity attestation**: `--by`, `approved_by` and similar labels are unverified declarations.
- There is no automatic approval, secret store, multi-user authorization, hosted product, automatic private-data extraction, or guarantee that an agent will comply with instructions.
- The fictional organisation is a demonstration, not a recommended deployment with real client or personal data. Review any material before putting it in an AI agent's context or publishing a repository.

## Licensing, community and credit

Living System's repository files are distributed under the **[Mozilla Public License 2.0](LICENSE)** (`MPL-2.0`). Covered modifications distributed to others are subject to the licence's obligations. Independently created files or organisational data are **not automatically MPL-covered merely because someone uses Living System**, though copying covered template material into them may affect the analysis. Read the licence for exact terms.

Copyright © 2026 Adrianna Mamczarz, for copyrightable original material to which she holds rights. The Trinity Tribe is the project home. Contributions are welcome under the repository licence; see [CONTRIBUTING.md](CONTRIBUTING.md). Please credit the creator and other contributors when discussing or building upon this work.

Forks and independent implementations are welcome, but should not imply official approval or affiliation with The Trinity Tribe. For vulnerability reporting, see [SECURITY.md](SECURITY.md).

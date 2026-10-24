# Living System docs

Status: EXPERIMENTAL. Version: 0.2.0.

Plain words first. Exact commands are under the heading that needs them. Every feature page answers the same ten questions, in the same order, using [the feature template](features/_template.md).

## Start here

- [AI tools](ai-tools.md): which AI tools work with Living System, what to install, what the permission prompts mean, and how to stay safe.
- [INSTALL.md](../INSTALL.md): the guided setup your agent follows when you say "Read INSTALL.md and set up my workspace."
- [README](../README.md): what Living System is and the quick start.
- [Ethics and guardrails](ethics.md): what Living System will not do, how each guardrail is upheld, and which ones a tool enforces.
- [How it is built](architecture.md): the workspace, who decides what, the four tools and the building blocks.
- [Command reference](cli.md): every command in plain words.
- [Troubleshooting](troubleshooting.md): common messages and what to do.
- [Brand](../brand/README.md): the mark, colours, type and images, a sibling of The Trinity Tribe's design system.
- [Local-first and resource use](local-first.md): what runs offline on your computer, what needs an AI agent, and what is not measured.

## Features

- [Workspace setup](features/workspace-setup.md): create your own private workspace in a separate folder, with a profile and a language.
- [Decisions and proposals](features/decisions-and-proposals.md): your rules are files, an agent can only propose changes, and only your review changes a rule.
- [Value check](features/value-check.md): a small before-and-after test you run yourself to see whether the system helps.
- [Handover note](features/handover-note.md): one file where the agent records where a session stopped, so the next session can continue.
- [Atlas](features/atlas.md): a map of which rules are in force and what relies on them, with a diagram.
- [Doctor](features/doctor.md): a read-only check that lists problems in your workspace in plain words.
- [Workflow generator](features/workflow-generator.md): create the folders for a staged workflow with a stop for you after each step.
- [Modules](features/modules.md): add and remove optional ready-made workflows, always with a plan first.
- [Status](features/status.md): a read-only list of what needs your attention.
- [Catch-up](features/catch-up.md): what changed while you were away, changed rules first.
- [Material from outside, and secrets](features/outside-material-and-secrets.md): outside e-mails and documents are checked for hidden instructions; passwords and keys stay out of the workspace.
- [Review record](features/review-record.md): every review is fingerprinted, so you can tell if an approved rule was changed afterwards.
- [Connected workspaces](features/connected-workspaces.md): a shared company workspace and private personal ones; role knowledge is handed on without personal information.
- [Onboarding path](features/onboarding.md): a private reading path through company rules, role knowledge and workflows, a few items at a time.
- [Parking, tending and checking ideas](features/parking-and-tending.md): focus mode, park an idea without switching task, tend what is waiting one item at a time, and decide what not to build.
- [Personal work agreement](features/work-agreement.md): your own plain-text agreement on how AI works with you, including what saved time is for.
- [Learning mode](features/learning-mode.md): coach mode, practice questions about your own rules, and a handbook for working without AI.
- [Upgrade](features/upgrade.md): bring a workspace up to date without overwriting your own edits.
- [Obsidian or any editor](features/obsidian.md): read and approve in a note app; what not to edit by hand.
- [Export](features/export.md): pack your whole workspace into one zip file, and restore it elsewhere.
- [Agency and delegation](features/agency.md): who may do what, honestly labelled, and delegation levels you grant and withdraw per kind of work.
- [Write guard](features/write-guard.md): stops the agent from editing your decisions or approving your drafts directly.
- [Third-Run counter](features/third-run-counter.md): counts repeated work and asks you at the third time whether to automate it.

## Modules

- [Weekly update](../modules/weekly-update/README.md): a three-step weekly update where you do the sending.
- [Meeting notes](../modules/meeting-notes/README.md): turns meeting notes into clean notes, actions and proposals.
- [Staged learning](../modules/staged-learning/README.md): lets your agent suggest lessons, and uses only the ones you approve.
- [Careful run](../modules/careful-run/README.md): bigger or riskier work in six checked steps, with a run card you can pause and resume safely.
- [Work audit](../modules/work-audit/README.md): look at how work really happens before adding AI, then test one small change.
- [Research review](../modules/research-review/README.md): answer a question from dated sources, with conflicts and gaps listed.
- [Client intake](../modules/client-intake/README.md): turn a new client's request into a clear picture and one next step.
- [Content preparation](../modules/content-prep/README.md): prepare a post or newsletter in checked steps; you publish.
- [Small experiment](../modules/small-experiment/README.md): try one change, measure it the same way before and after, and keep, revise or revert it.
- [Second check](../modules/second-check/README.md): important work gets an independent check before you decide.
- [Knowledge inbox](../modules/knowledge-inbox/README.md): keeps reusable knowledge with its source and reminds you to re-check old facts.

## For people who want to recommend it

- [Making the case](champions.md): honest arguments for CEOs, CTOs and founders, from your own evidence summary (`living.py evidence`).

## For contributors

- [Testing guide](../TESTING.md): a 30-minute path for first-time testers, and how to give feedback.
- [Contributing](../CONTRIBUTING.md) and the [code of conduct](../CODE_OF_CONDUCT.md).
- Release notes: [0.2.0 preview 2](releases/0.2.0-preview.2.md), [0.2.0 preview 1](releases/0.2.0-preview.1.md).

- [Evaluation: a small local decision model](evaluations/laya/README.md): Laya tested against keyword rules on 72 labelled requests; not adopted, with the numbers.
- [Roadmap and capability review](roadmap.md): what exists, what comes next, and what will not be built, with reasons.

- [Manual test checklist](testing-checklist.md): a step-by-step check of a release on a real computer, Windows first.
- [Changelog](../CHANGELOG.md): what changed in each version.
- [Feature template](features/_template.md): the ten headings every feature page keeps, in this order.
- [Credits](../CREDITS.md): who the ideas come from, including the Interpretable Context Methodology.

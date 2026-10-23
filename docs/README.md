# Living System docs

Status: EXPERIMENTAL. Version: 0.2.0.

Plain words first. Exact commands are under the heading that needs them. Every feature page answers the same ten questions, in the same order, using [the feature template](features/_template.md).

## Start here

- [AI tools](ai-tools.md): which AI tools work with Living System, what to install, what the permission prompts mean, and how to stay safe.
- [INSTALL.md](../INSTALL.md): the guided setup your agent follows when you say "Read INSTALL.md and set up my workspace."
- [README](../README.md): what Living System is and the quick start.

## Features

- [Workspace setup](features/workspace-setup.md): create your own private workspace in a separate folder, with a profile and a language.
- [Decisions and proposals](features/decisions-and-proposals.md): your rules are files, an agent can only propose changes, and only your review changes a rule.
- [Value check](features/value-check.md): a small before-and-after test you run yourself to see whether the system helps.
- [Handover note](features/handover-note.md): one file where the agent records where a session stopped, so the next session can continue.
- [Doctor](features/doctor.md): a read-only check that lists problems in your workspace in plain words.
- [Workflow generator](features/workflow-generator.md): create the folders for a staged workflow with a stop for you after each step.
- [Modules](features/modules.md): add and remove optional ready-made workflows, always with a plan first.
- [Status](features/status.md): a read-only list of what needs your attention.
- [Catch-up](features/catch-up.md): what changed while you were away, changed rules first.
- [Learning mode](features/learning-mode.md): coach mode, practice questions about your own rules, and a handbook for working without AI.
- [Upgrade](features/upgrade.md): bring a workspace up to date without overwriting your own edits.
- [Obsidian or any editor](features/obsidian.md): read and approve in a note app; what not to edit by hand.
- [Export](features/export.md): pack your whole workspace into one zip file, and restore it elsewhere.
- [Write guard](features/write-guard.md): stops the agent from editing your decisions or approving your drafts directly.
- [Third-Run counter](features/third-run-counter.md): counts repeated work and asks you at the third time whether to automate it.

## Modules

- [Weekly update](../modules/weekly-update/README.md): a three-step weekly update where you do the sending.
- [Meeting notes](../modules/meeting-notes/README.md): turns meeting notes into clean notes, actions and proposals.
- [Staged learning](../modules/staged-learning/README.md): lets your agent suggest lessons, and uses only the ones you approve.
- [Second check](../modules/second-check/README.md): important work gets an independent check before you decide.
- [Knowledge inbox](../modules/knowledge-inbox/README.md): keeps reusable knowledge with its source and reminds you to re-check old facts.

## For contributors

- [Manual test checklist](testing-checklist.md): a step-by-step check of a release on a real computer, Windows first.
- [Changelog](../CHANGELOG.md): what changed in each version.
- [Feature template](features/_template.md): the ten headings every feature page keeps, in this order.
- [Credits](../CREDITS.md): who the ideas come from, including the Interpretable Context Methodology.

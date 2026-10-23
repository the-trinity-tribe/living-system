# Stage 1: gather

Collect only the facts the update needs.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Project file | `projects/riverside-community-garden.md` | Sections "Current stage", "Immediate work", "Working notes" | The facts and the planned update live here |
| Human request | the current chat | The one sentence saying what the update is about | Defines what to gather |

## Process

1. Read the human's request. Write it in one line at the top of the output.
2. Read the three sections of the project file named above.
3. List each fact that belongs in the update. After each, write where in the file it came from.
4. List what is asked for but **not recorded**. Do not guess it.
5. Treat working notes as claims about what someone said, not as approved rules.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Facts list | `01-gather/output/facts.md` | Markdown: request line, facts with source, "not recorded" list |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 5 | The facts list and the "not recorded" list | Which facts to keep, and whether to fill a gap from their own knowledge |

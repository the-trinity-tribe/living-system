# Stage 1: capture

Clean up the raw notes. Add nothing.

## Inputs

| Source | File | Scope | Why |
| --- | --- | --- | --- |
| Human | Pasted notes, or a file the human names | All | The raw material |

## Process

1. Ask for the meeting date, the people present and the topic if the notes do not say.
2. Fix spelling and order. Group by topic.
3. Keep who said what exactly as written. If it is unclear, write "speaker not recorded".
4. Do not summarise away anything that sounds like a promise, a rule or a number.

## Outputs

| Artifact | Location | Format |
| --- | --- | --- |
| Clean notes | `01-capture/output/<date>-notes.md` | Markdown: date, people, topics, notes |

## Checkpoint

| After step | Agent presents | Human decides |
| --- | --- | --- |
| 4 | The clean notes | Correct them, then start stage 2, or stop |

# Feature: review record (was anything changed after approval?)

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

Every time you review a proposal, the review tool adds one line to `decisions/review-record.jsonl`. The line holds a fingerprint of each file the review wrote: the new decision and the reviewed proposal. `review.py verify` compares your files with those fingerprints and tells you if anything was changed or deleted afterwards.

## Why would someone need it?

Decisions are plain files. Anyone (a person, a script, an agent without the guard) can quietly change an approved rule. Without a record you cannot tell whether the text in front of you is what was approved.

## What problem does it solve?

- A changed approved decision is noticed, with the date it was approved.
- A rejected proposal set back to "proposed" by hand is noticed.
- A decision that did not come through review (written by hand) is pointed out, so you can check who wrote it.
- Each line is chained to the one before, so editing or removing an old line shows up too.

## What does it require?

A Living System workspace and Python 3.10 or newer. Nothing else.

## How do you install or enable it?

It starts by itself with your first review. A workspace that already has decisions can start it now; this records the files as they are today:

```sh
python3 tools/review.py verify --start --by "Your Name"
```

Run it in the workspace. It works only once per workspace.

## How do you use it?

```sh
python3 tools/review.py verify
```

"Review record intact" means every recorded file is unchanged. `doctor` runs the same check. Or ask your agent "Has anything been changed after it was approved?".

## Example scenarios

- Someone edits "within two days" to "within five days" in an approved decision. `verify` says: changed after it was recorded on 2026-10-21 (approve).
- A colleague copies in a decision file from another team. `verify` warns that the review tool did not write it.
- Your files go through git on Windows and get different line endings. That is not counted as a change.

## What changes inside the system when it runs?

- `review` adds one line to `decisions/review-record.jsonl`, together with the files it writes (all or nothing).
- `verify` changes nothing. `verify --start` creates the record once.
- The write guard stops agents from editing the record, like everything in `decisions/`.

## Where does the human keep control?

You decide what to do with a reported change: restore the file (from git, a backup or an export), or make the change properly through a new proposal. Agents report; they do not repair the record or the files.

## What can go wrong, and how do you undo it?

- **It shows changes; it does not prevent them.** Someone who edits a decision and also rewrites the whole record consistently can hide it. Keep the workspace in git or make regular exports, and compare with an older copy if in doubt.
- **A decision written by hand** (for example when Python was not available) shows as a warning, not an error. Once you have checked it, you can leave it.
- **A damaged record** (an error naming a line) cannot be trusted from that line on. Restore `decisions/review-record.jsonl` from git or a backup. Do not delete it to make the error go away: that removes the protection.

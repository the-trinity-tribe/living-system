# Feature: meeting notes workflow

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `meeting-notes`.

## What does this feature do?

It turns raw meeting or call notes into three things, one checked step at a time: clean notes, a list of actions and open questions, and proposals for anything someone said about how things should be done.

## Why would someone need it?

Meetings change rules informally ("from now on, Alex can sign that off"). Those changes get lost, or an AI later treats them as fact. This catches them and puts them in front of you to approve or reject.

## What problem does it solve?

- Decisions made in passing are no longer forgotten or repeated.
- An AI cannot quietly turn a remark into a rule: it can only stage a proposal.
- Actions keep their owner and date, or are marked "not recorded".

## What does it require?

A Living System workspace. No other modules. Claude Code or Codex.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace meeting-notes          # shows what would be added
python3 tools/living.py add ~/my-workspace meeting-notes --apply  # adds it
```

## How do you use it?

Paste your notes and say: "Run stage 1 of the meeting notes workflow." Check the clean notes, then ask for stage 2 and stage 3. Review any proposals it staged with `python3 tools/review.py review <proposal> --outcome approve|reject|defer --by "<your name>"`.

## Example scenarios

- A founder's call notes say a team member may now approve small refunds. Stage 3 stages a proposal instead of changing the rule.
- A team meeting produces six actions; two have no owner, and the extract says so.
- A student group agrees who submits the report; it becomes a `kind: new` proposal for their own workspace.

## What changes inside the system when it runs?

Each stage writes one file into its `output/` folder. Stage 3 may also create files in `proposals/`. Decisions never change unless you run the review command yourself.

## Where does the human keep control?

- After every stage you read, edit or stop.
- Only you approve proposals, with the review command.
- The workflow never shares or sends anything.

## What can go wrong, and how do you undo it?

- **A remark is misread as a rule:** reject the proposal. Nothing changed.
- **A proposal is broader than what was said:** edit it or reject it before review. The workflow is told to write the narrowest reading, but agents can get this wrong.
- **Remove it:** `python3 tools/living.py remove ~/my-workspace meeting-notes --apply`. Proposals it created stay; they are yours.
- **Limits:** the notes are only as reliable as whoever wrote them. Speaker attribution is never verified.

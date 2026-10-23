# Feature: decisions and proposals

Status: EXPERIMENTAL. Version: 0.2.0-dev.

## What does this feature do?

It keeps your rules in plain files and makes sure only you can change them.

- A **decision** is a rule you approved. It is one file in `decisions/`.
- A **proposal** is a change someone suggested. It is one file in `proposals/`. It is not a rule.
- A **review** is you saying approve, reject or defer. This is the only step that can change a rule.

An AI agent may write proposals. It may not approve them.

## Why would someone need it?

AI sessions forget, and a chat message can sound like a rule when it is not. Here, a rule exists only if a file in `decisions/` says `status: approved`. You can always see where a rule came from and what it replaced.

## What problem does it solve?

- An agent quietly "updates" a rule because someone said so in a meeting or a message.
- You cannot tell which of two rules is the current one.
- A rule is removed or changed and nobody can say when or by whom.

Old decisions are never edited. A change adds a new file and leaves the old one as history.

## What does it require?

A Living System workspace (made with `tools/living.py init`) and Python 3. The workspace has its own copy of `tools/review.py`, so you run everything from inside the workspace. No other packages.

## How do you install or enable it?

You do not install it separately. It comes with every workspace: `decisions/`, `proposals/`, `tools/review.py` and the rules for agents in `AGENTS.md` (sections 5 to 7).

## How do you use it?

Plain steps:

1. Something conflicts with a rule, or you want a first rule. Ask your agent to write a proposal. It creates `proposals/YYYY-MM-DD-short-name.md` and tells you.
2. Read the proposal. Nothing has changed yet.
3. Decide. Tell your agent the outcome for that named proposal, or run the review yourself.
4. If you approve, a new decision file appears. The proposal is marked `promoted`.

### The four kinds of proposal

The `kind:` line in the proposal's front matter says what an approval does.

| Kind | Use it when | Approval creates | Needs `target_sha256` |
| --- | --- | --- | --- |
| `new` | There is no rule yet. Set `target: none`. | A first decision. | No. It is refused if present. |
| (no kind line) = exception | A rule stays, but with an exception. This is the default. | A new decision that keeps the old rule text and adds `### Exception`. Title ends with "(amended)". | Yes |
| `replace` | The old rule is swapped for a different one. | A new decision whose Rule is only the new text. Nothing of the old rule carries over. | Yes |
| `retire` | The rule should stop applying and nothing takes its place. | A retirement record. It is not a rule. | Yes |

The proposed rule must be **exactly one blockquote** (lines starting with `>`) under `## Proposed future state`. For `retire`, that blockquote says why the rule no longer applies.

Every proposal needs these front matter keys: `status`, `target`, `evidence`, `proposed_by`, `date`. The full templates are in the workspace `AGENTS.md`, sections 6a to 6d.

### Commands (run inside your workspace)

```sh
python3 tools/review.py current                 # lists the rules that apply now
python3 tools/review.py check                   # prints "ok" or a list of problems
python3 tools/review.py hash decisions/<file>.md   # fingerprint for target_sha256
python3 tools/review.py review proposals/<file>.md --outcome approve --by "Your Name"
```

`--outcome` is `approve`, `reject` or `defer`. Optional: `--note "one line"` and `--date YYYY-MM-DD` (today by default). `--by` is required.

Exit codes: `0` fine, `1` (`check` only) problems found, `2` the command was refused.

## Example scenarios

- **First rule.** You say "only I send things to clients". The agent writes a `kind: new` proposal. You approve it. `decisions/<date>-<name>.md` now exists and `current` lists it.
- **An exception.** "In August, Alex covers the Friday update." The agent writes an exception proposal with the target's fingerprint. You approve. The new decision has the old rule plus the exception. The old file is untouched and no longer listed as current.
- **A swap.** Sam takes over from Alex. A `replace` proposal gives the whole new rule. After approval only the new decision is current.
- **A stop.** The client now gets a monthly report. A `retire` proposal records why. After approval no rule applies on that matter. If you want a rule back later, write a `kind: new` proposal.

(Names are made up for this page.)

## What changes inside the system when it runs?

**Reject or defer:** only the proposal changes. Its `status` becomes `rejected` or `deferred`. No decision changes. A rejected proposal is closed. A deferred one can be reviewed again.

**Approve:**

- One new file in `decisions/`, named `<review date>-<rest of the proposal's file name>.md`. The proposal's file name must therefore start with `YYYY-MM-DD-`.
- The new decision carries `status: approved`, `approved_by`, `date`, `source_proposal:` and, for exception, replace and retire, `supersedes:` pointing at the old decision.
- The proposal becomes `promoted`. It gains `reviewed_by`, `reviewed_on`, `resulting_decision` and a line in a `## Review log` section.

A decision is **current** when it is approved and no other approved decision names it in `supersedes:`. A retirement record (`kind: retirement`) is never listed as current and is never a rule. It cannot be amended, replaced or retired. `current` lists only current rules.

Writes are all-or-nothing. If something fails halfway, the tool undoes what it wrote. It never overwrites an existing decision file.

A promoted proposal is history. The decision it created is the source of truth, not the proposal's old open questions.

## Where does the human keep control?

- Only a review with `--outcome approve` changes a rule. Notes, messages and proposals do not.
- Your agent must not run the review on its own guess, and must not run it because you asked it to build or test the tool. It runs it only when you state the outcome for a named proposal (`AGENTS.md` section 7).
- `--by "Name"` is **attribution, not identity**. The tool does not check who typed it. Anyone with access to the folder can type any name. The same goes for `approved_by` and `reviewed_by`.
- The tool never edits an old decision.

### When the tool refuses

A refusal prints `REFUSED: <reason>` and writes nothing. After a refusal a human must look again. Do not work around it.

- The proposal is already `promoted` or `rejected`, or its status is not `proposed` or `deferred`.
- **Hash mismatch:** the target decision changed after the proposal was written. Re-check it, then write or update the proposal with the new fingerprint.
- **Superseded target:** another approved decision already replaced the target.
- The target is not approved, is missing, or is a retirement record.
- **Malformed rule:** not exactly one blockquote, empty, a line inside it not starting with `>`, a code block, a heading, or a `---` line inside the rule.
- For `new` and `replace`: no single `# Proposal: <title>` line. For exception and retire: the target has no title. For exception: the target lacks exactly one each of `## Rule`, `## Why`, `## Scope`.
- `kind` and `target` do not fit: `kind: new` needs `target: none` and no hash; `target: none` needs `kind: new`; unknown kinds are refused.
- **Line breaks and control characters** in `--by`, `--note`, a path or the proposal title.
- **Links:** `proposals/` or `decisions/` is a symbolic link, or the proposal file or the new decision path is a link.
- Odd paths: `./`, `..`, `//`, a backslash, or a sub-folder. Write `proposals/<name>.md`.
- The new decision file already exists, even if it appeared while the review ran.
- **One review at a time:** the tool creates `.review.lock` in the workspace root while it works. If the file exists, it refuses. If no review is running, delete `.review.lock` and try again.
- `--by` is blank, or `--date` is not `YYYY-MM-DD`.

Even `reject` and `defer` need a sound proposal: its own front matter and its target path are checked first.

## What can go wrong, and how do you undo it?

- **Approved the wrong thing.** Decisions are not edited. Write a new proposal (`replace`, `retire`, or an exception) and approve that. The mistake stays in the history.
- **A proposal was rejected by mistake.** A rejected proposal is closed. Write a new one.
- **Edited a decision by hand.** The tools do not detect this. `check` does not compare decisions with a stored fingerprint. Keep the workspace in Git if you want to see changes.
- **`check` prints problems.** It reports, among other things, unexpected status values, a `supersedes:` pointing at a missing file, a retirement record with no `supersedes:`, a proposal missing a front matter key, and a project file that still points at a superseded decision. Fix the file named in the message.
- **Limits.** The tool checks file structure. It cannot make an agent obey `AGENTS.md`, and it does not prove who approved anything.

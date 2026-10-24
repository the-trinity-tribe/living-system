# Feature: agency and delegation

Status: EXPERIMENTAL. Version: 0.3.0-preview.

## What does this feature do?

Two things:

- **`living.py agency`** shows, in one page, who may do what in your workspace: who proposes, who approves, what the write guard blocks, what always needs your yes, and what you have delegated. Every line says whether a **tool enforces it** or it is an **instruction** to the agent.
- **Delegation levels** let you give the agent more room for one kind of work at a time, and take it back:

| Level | The agent... |
| --- | --- |
| observe | may read and report only |
| recommend | may suggest; you do it |
| draft | may prepare it; you check and use it (**the default for everything**) |
| act-with-approval | may do it after your yes, each time |
| bounded | may do it without asking, inside a stated scope, until a review date |

## Why would someone need it?

Trust in an AI agent should be specific, earned and reversible. "The agent may tidy the headings in my knowledge files" is very different from "the agent may do things". And people need to know which limits are real technical blocks and which depend on the agent following instructions.

## What problem does it solve?

- You can see your agent's limits in one place, honestly labelled.
- More autonomy is granted for one kind of work, with evidence, never across the board.
- Withdrawing it is one step, and the history stays.

## What does it require?

A Living System workspace and Python 3.10 or newer. Delegations are followed by Claude Code or Codex.

## How do you install or enable it?

Nothing to install.

```sh
python3 tools/living.py agency ~/my-workspace
python3 tools/living.py delegate ~/my-workspace "weekly update drafts" draft --evidence "five drafts used unchanged"
```

## How do you use it?

1. When work has gone well several times, you (or the agent, once) suggest a level with `delegate`. It shows the proposal; add `--apply` to write it.
2. You review it like any proposal: `python3 tools/review.py review proposals/<file> --outcome approve --by "Your Name"`. Only then is it in force.
3. `bounded` needs a scope and a review date at most 90 days away. When the date comes, `status` and the agent remind you.
4. To withdraw it, retire the decision (`living.py propose . --kind retire --target <decision> ...`).

## Example scenarios

- After six weekly updates you used unchanged, you delegate "weekly update drafts" at `draft`, and later "weekly update facts gathering" at `bounded`, with the scope "read project files only" and a review in six weeks.
- You try to delegate "send client emails" at `bounded`. The tool refuses: sending always keeps your yes; the highest level for it is `act-with-approval`.
- A new colleague asks what the agent may do in the team workspace. `agency` shows it, including that the team rule is enforced and the delegations are instructions.

## What changes inside the system when it runs?

- `agency` changes nothing.
- `delegate --apply` writes one proposal in `proposals/`. Approving it creates a normal decision whose rule starts with `Delegation:`, recorded in the review record like any other.

## Where does the human keep control?

- Nothing is delegated until you approve the proposal.
- Publishing, sending or messaging people, spending, deleting, signing and changing rules can never go above `act-with-approval`.
- A delegation never lifts the write guard or the review rules.
- You can withdraw any delegation by retiring it.

## What can go wrong, and how do you undo it?

- **Delegations are instructions, not technical permissions.** The agent is told to stay within them; no tool watches what it does inside a level. The lines marked `[enforced]` in `agency` are the ones a tool actually checks.
- **A delegation is worded too broadly.** Retire it and propose a narrower one. When the agent is unsure which level applies, it uses the lower one.
- **Names are labels.** There is no login or identity check; see [connected workspaces](connected-workspaces.md) for what that means in a team.

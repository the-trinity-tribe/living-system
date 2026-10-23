# Feature: connected workspaces (personal and company)

Status: EXPERIMENTAL. Version: 0.2.0.

## What does this feature do?

A company keeps one shared **company workspace**. Each person keeps their own private **personal workspace** and links it to the company one, with their role. Then:

- The company's approved rules apply to everyone's company work, and come before personal rules.
- People hand on what they learned in their role (knowledge, lessons, workflows) to the company workspace, without personal information. Someone in the company accepts or rejects it.
- The next person in the same role finds that knowledge in `roles/<role>/knowledge/` and does not start from zero.
- In the company workspace, whoever proposed a change never approves it, and whoever shared knowledge never accepts it.

Nothing is synced, uploaded or sent. Both are folders on your computers; the company one is typically shared through git or a shared drive.

## Why would someone need it?

When someone leaves a role, most of what they learned leaves with them. The next person asks the same questions and makes the same mistakes. And when each person's AI only knows that person's notes, the company's rules are explained again and again.

## What problem does it solve?

- One set of company rules, read by every person's agent.
- Role knowledge survives a change of person.
- Private things stay private: your goals, notes and handover stay in your workspace.
- Nobody approves their own change in the shared workspace.

## What does it require?

Two Living System workspaces and Python 3.10 or newer. The company workspace must be reachable as a folder on each person's computer (for example a git clone or a synced folder).

## How do you install or enable it?

1. Once, a manager creates the company workspace:

```sh
python3 tools/living.py init ~/company --profile manager --language en --team
```

2. Each person links their own workspace, with their role (a short name, never a person's name):

```sh
python3 tools/living.py link ~/my-workspace --org ~/company --role account-manager
```

Undo: `living.py link ~/my-workspace --remove`.

## How do you use it?

- **Hand something on.** Say "share this with the team". The agent shows exactly what would be written; after your yes it runs:

```sh
python3 tools/living.py share ~/my-workspace knowledge/pricing.md --apply
```

Only files in `knowledge/`, `workflows/` or `lessons/active.md` can be shared. A file with an e-mail address, phone number, bank account number, password or text addressed to an AI is refused until you remove it.

- **Accept or reject it** (someone else, in the company workspace). `status` lists what waits:

```sh
python3 tools/living.py role-review ~/company roles/account-manager/inbox/2026-10-24-pricing.md --outcome accept --by "Kim Lead"
```

Accepting moves it to `roles/account-manager/knowledge/`. Rejecting deletes the shared copy; the original stays in the sharer's workspace.

- **Stay up to date.** `status` shows how many company rules are in force; `since` (catch-up) lists company rule changes while you were away.

## Example scenarios

- An account manager learned which questions clients ask in Q4. They share it; the team lead accepts it. The next account manager's agent reads it from day one.
- A shared note contains a client's phone number. `share` refuses and names the line; the person rewrites it as "call the client's main contact".
- The team lead proposes a new discount rule in the company workspace. `review.py` refuses their own approval; a colleague reviews it.

## What changes inside the system when it runs?

- `link` writes `org_folder` to `.living/local.json` (this computer only, never shared) and `role` to `.living/profile.json`.
- `share` writes one file into `roles/<role>/inbox/` of the company workspace, with `status: proposed`, the role label and the date. It never changes the original.
- `role-review` moves an accepted file to `roles/<role>/knowledge/` with who accepted it and when, or deletes a rejected one.
- The write guard stops agents in a personal workspace from writing into the company folder, and agents in the company workspace from editing shared role knowledge by hand.

## Where does the human keep control?

- Nothing is shared without a preview and your yes.
- Nothing becomes company knowledge until a person in the company accepts it, and that person is not the one who shared it.
- Accepted role knowledge is background (level 4), never a rule. Rules change only through proposals and review.

## What can go wrong, and how do you undo it?

- **Names are not detected.** The tool catches contact details, account numbers and secrets, not names of people or clients. Read the preview.
- **Names in `--by` are labels, not proof of identity.** Anyone can type any name. For real accountability, use the company's git history or shared-drive permissions as well.
- **The company folder moves.** `doctor` and `status` say the link is broken; link again.
- **Something was accepted by mistake.** Delete it from `roles/<role>/knowledge/` by hand in the company workspace (agents may not).

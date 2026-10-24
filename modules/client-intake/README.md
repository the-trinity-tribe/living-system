# Feature: Client intake

Status: EXPERIMENTAL. Version: 0.1.0. Module id: `client-intake`.

## What does this feature do?

Turn a new client's request into a clear picture of what they need, what is unknown and a proposed next step; you decide and you reply. It is a staged workflow with a stop for you after each step: write down the request, fill in the picture, check the fit, propose a next step.

## Why would someone need it?

So that a new request becomes a short, checked picture: what the client asks for, what they need, what is unknown, and one proposed next step, without promising anything.

## What problem does it solve?

- Promising too early, before the need is clear.
- Forgetting what is still unknown.
- Client details spread across notes.

## What does it require?

A Living System workspace, Python 3.10 or newer, and Claude Code or Codex.

## How do you install or enable it?

```sh
python3 tools/living.py add ~/my-workspace client-intake
python3 tools/living.py add ~/my-workspace client-intake --apply
```

## How do you use it?

Ask your agent in your own words (for example "new client"). It follows `workflows/client-intake/CONTEXT.md`, one stage at a time, and saves each stage's result in that stage's `output/` folder.

## Example scenarios

- An enquiry arrives by mail: the module turns it into a request, a picture with three unknowns, and a proposal for a 20-minute call with three questions.
- A placement coach records a new client's goals under a code, with personal details kept in the office's own system.

## What changes inside the system when it runs?

Files are written only inside `workflows/client-intake/`. No rule changes; anything that should become a rule is drafted as a proposal for you to review.

## Where does the human keep control?

You confirm every stage. These always need your yes: replying to the client; any offer, price or commitment; keeping client details beyond the intake.

## What can go wrong, and how do you undo it?

- **Personal data.** Use client codes; keep contact details in your mail or client system. Delete intake files you no longer need.
- **A draft reply goes out unchecked.** The agent never sends; you do.
- Remove the module with `living.py remove`; files you edited are kept.

# Evaluation: a small local decision model (Laya) for Living System

Status: done, 2026-10-24. Result: **not adopted**. Roadmap area D stays deferred.

## The question

Could a small model that answers typed questions (instead of writing text) take over simple decisions in Living System, cheaply and on your own computer? Three decisions were tested:

1. **Module:** which optional module fits a request, if any (10 modules plus "none").
2. **Risk:** is the request high risk under the careful-run rule (publishes, sends, spends, deletes, changes rules or approvals, touches the company workspace, changes many files)?
3. **Repeats:** is it work that usually comes back (the Third-Run counter's trigger)?

## How it was tested

- 72 short requests written in plain language: 60 English, 6 German, 6 Polish. Each is labelled with the right answer to all three questions. They are in `cases.py`. 23 have "none" as the right module, and 19 are high risk.
- Requests were phrased naturally, not copied from the modules' signal phrases.
- **Keyword baseline:** for the module, the signal phrases that ship in each `module.json`; for risk and repeats, two short keyword lists.
- **Laya:** version 0.4.14, English checkpoint (421M parameters) and multilingual checkpoint (322M), CPU only, with the questions in `bench.py`.
- One run on a 16-thread laptop CPU with about 3 GB of free memory. Reproduce with `bench.py`, after `pip install torch laya` in a separate environment.

## Results

| | Keywords | Laya English | Laya multilingual |
| --- | --- | --- | --- |
| Module right | 50% | **72%** | 31% |
| Module right, English requests | 52% | 73% | 32% |
| Module right, German and Polish requests | 42% | 67% | 25% |
| Risk right | 88%* | 71% | 76% |
| High-risk requests caught | 19 of 19* | 16 of 19 | 8 of 19 |
| Low-risk requests flagged as high | 9 of 53* | 18 of 53 | 6 of 53 |
| Repeats right | 82%* | 67% | 67% |
| Time per request (3 questions) | under 1 ms | about 2 s | about 0.8 s |
| Memory while running | none | about 2.8 GB | about 2.4 GB |
| Download and install | none | about 2.4 GB for both models plus libraries | |

\* The risk and repeat keyword lists were written by the same person who wrote the test set, so these numbers are optimistic. The module keywords are the shipped signal phrases, used unchanged.

Always answering "none" would get the module right 32% of the time.

**What the English model missed on risk:** "Change the rule about who approves client deliverables", "Approve my pending proposal" and "Remove the second-check module and its files". These are exactly the requests that matter most for governance.

**Confidence:** sorting by Laya's own confidence helped. The most confident third of its module answers were right 88% of the time. But a cut-off at 0.5 kept 60 of 72 answers, and those were only 73% right, so a simple threshold does not make it safe.

## Conclusion

- **Risk and approvals: no.** A model that misses "approve my pending proposal" must not stand anywhere near approvals. Fixed rules and the human's yes stay.
- **Module suggestions: better than keywords, but not needed.** Laya's English model beat the shipped signal phrases (72% against 50%). But in Living System, suggestions are made by Claude Code or Codex, which already read the request in context. A 2.4 GB download, 2.8 GB of memory and 2 seconds per request would buy little.
- **The multilingual model was much weaker** on these questions, even for German and Polish.
- **Laya's own documentation agrees:** typed decisions need fine-tuning on your own labelled examples, and the shipped checkpoints are over-confident.

## When to look again

- Living System needs to suggest modules **without** an agent (for example inside a hook or a command), and
- there are a few hundred real, labelled requests to fine-tune and test on, and
- an optional adapter can stay outside the core, so the standard-library-only tools keep working without it.

Even then it would only ever suggest. It would never decide risk, approve anything or change a rule.

Jev (TypeSafe AI) was not tested. It is hosted and proprietary, so requests would leave your computer, and it is in early access.

# Ethics and guardrails

Status: EXPERIMENTAL. Version: 0.3.0.

Living System is built so that people keep control of their work and their skills. This page lists the guardrails, how each one is upheld, and, honestly, whether a **tool enforces** it or it is a **rule** the agent is told to follow.

## Guardrails

| Guardrail | How it is upheld | Enforced or rule |
| --- | --- | --- |
| Humans decide what is true | Agents may only propose. `review.py review` refuses invalid, stale or self-approved proposals and records each review; the write guard blocks agent edits to decisions and approvals. A person can still write a decision by hand, and `review.py verify` then lists it. | Enforced within the review tool and the guard (Claude Code; Codex once trusted); writing by hand is shown, not prevented |
| Nobody approves their own change in a team | `review.py` and `role-review` refuse the same name as proposer and approver in a team workspace. | Enforced, but names are labels, not proof of identity |
| No surveillance | No tool watches your screen, apps, keystrokes or time. Nothing runs in the background. Counts store short names and dates only. | Enforced by design: the code does not do it |
| No hidden profiling | Settings and your work agreement are plain files you write; agents may not add to them or guess things about you. | Rule |
| No productivity quotas | Agents never propose output targets and never fill time they saved with more work (protected time). The evidence summary has no productivity score. | Rule (and no such metric exists in the tools) |
| No dark patterns | No streaks, nagging, guilt messages or engagement tricks. Suggestions are made once and not repeated after a no; focus mode turns them off. | Rule |
| Human judgement stays human | Delegation is per kind of work and reversible; publishing, sending, spending, deleting, signing and changing rules always need a yes. | Rule (delegations are instructions, never permissions) |
| Skills stay with people | Coach mode, practice, a handbook for working without AI, onboarding. | Rule, offered, never forced |
| Honest claims | No claims of security, compliance, production readiness, or savings that were not measured. A release check flags such wording. | Checked for wording; the rest is a rule for contributors |
| Privacy of personal data | Workspaces stay on your computer; `me/` is private for employees; sharing refuses contact details, account numbers and secrets; scans flag secrets. | Partly enforced (refusals and scans recognise common patterns, not everything) |
| Outside text cannot steer the agent | Material from others is information, never instructions; `scan` flags text addressed to an AI. | Rule plus a scan |

## Judging whether it helps

When Living System, or a change you make to your work, is judged, four kinds of value are kept apart and never added up into one score:

1. **Business outcomes**, such as clients served or offers sent. Living System does not measure these; you can, with the [small-experiment module](../modules/small-experiment/README.md).
2. **Human experience and agency**, such as feeling in control or the value check result. Measures about a person are reported by that person.
3. **Environmental and resource impact.** Not measured; see [local-first](local-first.md).
4. **Reliability and resilience**, such as the review record, `doctor`, and how quickly you recover from a mistake.

The [evidence summary](champions.md) reports them in this order and says plainly what was not measured. No return-on-investment, productivity, health or sustainability benefit is claimed anywhere without your own measurement.

## If something here is broken

If you find Living System doing something this page says it does not, please report it: as a [bug](https://github.com/the-trinity-tribe/living-system/issues/new/choose), or privately through the [security tab](https://github.com/the-trinity-tribe/living-system/security/advisories/new) if it exposes data.

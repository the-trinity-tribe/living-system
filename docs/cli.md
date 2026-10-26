# Command reference

Status: EXPERIMENTAL. Version: 0.3.0.

Every command, in plain words. Run them from the Living System folder; on Windows type `py` instead of `python3`. Several commands show a plan first and change nothing until you add `--apply`; their description says so. Full options: `python3 tools/living.py <command> --help`.

## Set up and update

| Command | What it does |
| --- | --- |
| `living.py init --profile {student,professional,employee,manager} --language LANGUAGE [--calm-replies] [--coach] [--team] [--review-every RHYTHM] [--review-mode {batch,ask-now}] dir` | create a new workspace in a new folder |
| `living.py upgrade [--apply] workspace` | plan (or with --apply, apply) updates from this Living System version |
| `living.py protect [--apply] workspace` | put back a missing write guard or hook file (plan unless --apply) |
| `living.py menu` | the everyday commands, in plain words |

## Every day

| Command | What it does |
| --- | --- |
| `living.py status workspace` | what needs your attention, in plain words (read-only) |
| `living.py since (--date DATE \| --days DAYS) workspace` | what changed while you were away, rules first (read-only) |
| `living.py park [--done N] [--decide DECIDE] [--again DATE] workspace [idea]` | write an idea down without switching task, or list and tick off parked ideas |
| `living.py focus workspace {on,off}` | focus mode: the agent does what you ask and suggests nothing else |
| `living.py review-rhythm [--every RHYTHM] [--mode {batch,ask-now}] workspace` | show or set how often a review is due, and whether the agent asks now or leaves it for a batch |
| `living.py nudge workspace` | one calm line if a review is due, at most once a day; nothing otherwise |
| `living.py reviewed workspace` | note that you looked over what was waiting today |
| `living.py onboard [--done ID] [--next NEXT] workspace` | your reading path: company rules, role knowledge, workflows, a few at a time |

## Rules and agency

| Command | What it does |
| --- | --- |
| `living.py propose --kind {new,exception,replace,retire} --title TITLE --rule RULE --evidence EVIDENCE [--why WHY] [--by BY] [--target TARGET] [--apply] workspace` | plan (or with --apply, write) a proposal; never approves anything |
| `living.py delegate --evidence EVIDENCE [--scope SCOPE] [--review REVIEW] [--by BY] [--apply] workspace work {observe,recommend,draft,act-with-approval,bounded}` | propose a delegation level for one kind of work (plan unless --apply) |
| `living.py agency workspace` | who may do what here: enforced by a tool, or an instruction (read-only) |

## Knowledge and health

| Command | What it does |
| --- | --- |
| `living.py doctor [--out OUT] workspace` | read-only health check of a workspace |
| `living.py scan workspace [paths ...]` | look for secrets and hidden instructions in workspace files (read-only) |
| `living.py compost --reason REASON [--apply] workspace file` | move a knowledge file to knowledge/archive/ with a reason (plan unless --apply) |
| `living.py atlas [--out OUT] workspace` | a map of how rules, projects, workflows and knowledge connect (read-only) |
| `living.py handbook [--out OUT] workspace` | a readable copy of your rules and workflows, for working without AI |
| `living.py evidence [--out OUT] workspace` | counts you can show others: value check, reviews, repeated work (no content) |
| `living.py value-score workspace` | count right/wrong/made up/don't know in value-check/questions.md |

## Repeated work and modules

| Command | What it does |
| --- | --- |
| `living.py runs [--add NAME \| --decide NAME DECISION \| --forget NAME] [--after AFTER] workspace` | Third-Run Rule: count a kind of work, record a decision, or list counts |
| `living.py modules [--workspace WORKSPACE]` | list optional modules |
| `living.py add [--apply] workspace module` | plan (or with --apply, install) a module |
| `living.py remove [--apply] workspace module` | plan (or with --apply, remove) a module |
| `living.py new-workflow --stages STAGES [--goal GOAL] [--apply] workspace name` | plan (or with --apply, create) a staged workflow folder |
| `living.py checkpoint [--record] workspace card` | careful-run: record or compare fingerprints of a run card's files |

## Teams

| Command | What it does |
| --- | --- |
| `living.py link [--org ORG] [--role ROLE] [--remove] workspace` | link this personal workspace to a company workspace, with your role there |
| `living.py share [--as SHARED_AS] [--apply] [--withdraw] workspace file` | hand one file of role knowledge to the company workspace (plan unless --apply) |
| `living.py role-review --outcome {accept,reject} --by BY workspace file` | in a company workspace: accept or reject shared role knowledge |

## Backups

| Command | What it does |
| --- | --- |
| `living.py export [--apply] workspace file` | pack the workspace into one zip file (plan unless --apply) |
| `living.py export-check file` | check that an export zip holds a complete workspace (read-only) |

## The review tool

| Command | What it does |
| --- | --- |
| `python3 tools/review.py current` | List the decisions in force. |
| `python3 tools/review.py history` | Every decision, oldest first, with what replaced it. |
| `python3 tools/review.py check` | Structural checks of decisions, proposals and routing. |
| `python3 tools/review.py verify [--start --by NAME]` | Show anything changed after it was approved; start the record once. |
| `python3 tools/review.py hash <file>` | The fingerprint a proposal pins its target with. |
| `python3 tools/review.py review <proposal> --outcome approve\|reject\|defer --by NAME` | Record a human's decision on a named proposal. Changes files; run only when the human has decided. |

Run `review.py` inside a workspace (it uses its own folder), or add `--root <workspace>`.

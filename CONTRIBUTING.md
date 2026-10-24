# Contributing to Living System

Thank you for helping. Living System is experimental, and contributions of every size are welcome: a typo, a clearer sentence, a test report from Windows, a bug fix, a module, a translation review.

Testing and feedback count as contributions too: see [TESTING.md](TESTING.md).

## Ways to help

- **Test and tell us** what worked and what confused you ([feedback form](https://github.com/the-trinity-tribe/living-system/issues/new/choose)).
- **Review the German or Polish texts** in `core/i18n/de/` and `core/i18n/pl/`. Native speakers especially welcome.
- **Fix a bug** or improve a doc page.
- **Propose a module** for repeated work you know well. Modules are plain files; see `modules/` and [docs/features/modules.md](docs/features/modules.md).

For anything larger than a small fix, please **open an issue first**, so we can agree that it fits before you spend time on it. The [roadmap](docs/roadmap.md) lists what is planned, deferred and deliberately rejected, with reasons.

## Getting set up

You need Git and Python 3.10 or newer. Nothing else.

```sh
git clone https://github.com/the-trinity-tribe/living-system.git
cd living-system
python3 -B -m unittest discover tests
```

How the repository is laid out:

| Folder | What lives there |
| --- | --- |
| `tools/` | `living.py` (workspaces, modules, status, scans and more), `review.py` (rules and reviews), `guard.py` (the write guard), `release_check.py` |
| `core/template/` | The base workspace, including the agent rules in `AGENTS.md` |
| `core/profiles/`, `core/i18n/` | Profile overlays and German and Polish starter files |
| `core/skills/` | Shared skills, copied to Claude Code and Codex |
| `modules/` | Optional modules: `module.json`, `README.md`, `files/` |
| `demo/` | The fictional sandbox; never real data |
| `docs/` | One page per feature, the roadmap, the testing checklist |
| `tests/` | The test suite (standard `unittest`) |

## Ground rules

- **Standard library only.** No new dependencies for the tools.
- **Plain words first.** Docs are written for someone who is not technical; exact commands go under the heading that needs them. Feature pages follow [docs/features/_template.md](docs/features/_template.md).
- **Every behaviour has a test,** including what must be refused. A refusal writes nothing.
- **Humans decide.** Do not add anything that lets an agent approve, accept or change a rule on its own, or that weakens the write guard.
- **No real data.** No personal, client or company data, credentials, session transcripts or private material, in code, tests, docs or the demo. `tools/release_check.py` looks for common slips.
- **History stays.** Never edit approved decisions or the demo's history to make a test pass.
- **No invented claims.** Do not describe it as secure, compliant or production-ready, and do not add numbers for savings that were not measured.

## Before you open a pull request

```sh
python3 -B -m unittest discover tests
python3 -B tools/release_check.py
python3 -B tools/review.py --root demo/moss-and-circuit check
```

All three must pass. The automatic tests also run on Linux, Windows and macOS when you open the pull request. Add a line to `CHANGELOG.md` under the newest version at the top, in plain words.

Commit messages: short, plain, present tense (for example `fix: status shows parked ideas`). Please do not add automatic AI co-author lines.

## AI-assisted contributions

Welcome, if you have read and understood the change, can explain it, and mention material AI assistance in the pull request.

## Licence

By contributing, you agree to license your contribution under the repository's **MPL-2.0** terms, to the extent you hold rights to it. You keep your copyright. Keep existing notices. Maintainers decide what is merged. No contributor licence agreement or sign-off is required at this stage; if that changes, it will be announced openly.

## Behaviour

Be kind and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## What and why

<!-- What does this change, and what problem does it solve? Link the issue if there is one. -->

## How it was checked

- [ ] `python3 -B -m unittest discover tests` passes
- [ ] `python3 -B tools/release_check.py` finds nothing
- [ ] `python3 -B tools/review.py --root demo/moss-and-circuit check` says `ok`
- [ ] New behaviour has a test, including what should be refused
- [ ] Docs updated (a feature page follows `docs/features/_template.md`; `CHANGELOG.md` has a line)

## Ground rules

- [ ] Standard library only; no new dependencies
- [ ] No real personal, client or company data, no credentials, no private material
- [ ] Approved decisions and the demo's history are not edited to make a test pass
- [ ] AI assistance, if material, is mentioned here, and I can explain the change

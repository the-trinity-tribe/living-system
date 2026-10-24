# Live scenario tests

`run_live.py` checks how Claude Code and Codex actually behave in a Living System workspace: 13 everyday scenarios, each in a fresh copy of a prepared company workspace and a linked personal workspace.

It is **not** part of the automatic tests: it starts real agent sessions (which cost money) and needs `claude` and `codex` installed and signed in.

```sh
python3 tests/live/run_live.py setup
python3 tests/live/run_live.py run claude
python3 tests/live/run_live.py run codex
python3 tests/live/run_live.py report
```

Results are written to `live-runs/` (or `$LIVE_DIR`), which git ignores. The latest recorded results are in `demo/WALKTHROUGH.md`.

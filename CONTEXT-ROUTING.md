# CONTEXT-ROUTING.md

This is the **product** folder. It holds no organisation's rules. **Start with the smallest route. Expand context only when the task requires it.**

| Need | Read |
| --- | --- |
| What this project is and how to try it | `README.md` |
| Set up a person's own workspace (guided) | `INSTALL.md` |
| Explore the fictional demo organisation | `demo/moss-and-circuit/AGENTS.md`, then its `CONTEXT-ROUTING.md` (run its tools with `--root demo/moss-and-circuit`) |
| Show the system live | `demo/WALKTHROUGH.md` (keep it out of folders you give to a test agent) |
| Optional modules and what each does | `modules/<id>/README.md` and `modules/<id>/module.json` |
| What a new workspace starts with | `core/template/` and `core/profiles/<profile>/` |
| The tools | `tools/review.py` (decisions and proposals), `tools/living.py` (workspaces, modules, workflows, doctor) |
| Documenting a feature | `docs/features/_template.md` |
| Credits and influences | `CREDITS.md` |

Tips:

- Questions about an organisation's rules belong in that organisation's workspace or in the demo, never here.
- To change how the tools behave, read the matching tests in `tests/` first.

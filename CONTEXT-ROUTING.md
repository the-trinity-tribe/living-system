# CONTEXT-ROUTING.md

**Start with the smallest route. Expand context only when the task requires it.**

| Need | Read |
| --- | --- |
| Organisation identity, people, roles | `SYSTEM.md` |
| Governing principle | `PRINCIPLES.md` |
| Approved organisational choice (who approves what, how things must be done) | The relevant **current** file in `decisions/` (skip any decision named in another approved decision's `supersedes:`; `python3 tools/review.py current` lists them) |
| Reusable service knowledge | The relevant file in `knowledge/` |
| Current project | The relevant file in `projects/` |
| Suggested changes waiting for human review (not current truth) | `proposals/`: read when asked what is pending, or before creating a proposal |
| Narrative background for humans new to the example | `examples/moss-and-circuit.md` (optional, not authoritative) |

Tips:

- For a project task, start with the project file. It links to the decisions that apply.
- Anything about approvals is a decision question. Check `decisions/`, not role descriptions.

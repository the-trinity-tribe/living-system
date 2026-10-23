# CONTEXT-ROUTING.md

**Start with the smallest route. Expand context only when the task requires it.**

| Need | Read |
| --- | --- |
| Who the owner is, roles | `SYSTEM.md` (only canonical if `status: approved`) |
| Governing principles | `PRINCIPLES.md` (only canonical if `status: approved`) |
| Approved choice (who approves what, how things must be done) | The relevant **current** file in `decisions/` (skip any decision named in another approved decision's `supersedes:`; `python3 tools/review.py current` lists them) |
| Reusable knowledge | The relevant file in `knowledge/` |
| Current project | The relevant file in `projects/` |
| Repeated work that has a staged workflow | The relevant folder in `workflows/` |
| Suggested changes waiting for human review (not current truth) | `proposals/`: read when asked what is pending, or before creating a proposal |
| Where the last session stopped (not canonical) | `handover/LATEST.md` |
| Does the system help? (the owner's own check) | `value-check/README.md` |
<!-- profile:append -->

Tips:

- For a project task, start with the project file. It links to the decisions that apply.
- Anything about approvals is a decision question. Check `decisions/`, not role descriptions.

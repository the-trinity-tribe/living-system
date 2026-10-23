"""Doctor's knowledge upkeep: replaced references, duplicates, drawers, long instructions."""
import sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def proposal(title, kind="new", target="none", sha=None):
    extra = f"target_sha256: {sha}\n" if sha else ""
    return (f"---\nstatus: proposed\nkind: {kind}\ntarget: {target}\n{extra}evidence: e\nproposed_by: a\ndate: 2026-10-20\n"
            f"---\n\n# Proposal: {title}\n\n## Proposed future state\n\n> {title}.\n\n## Why and open questions\n\nt\n")


class TestUpkeep(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def notes(self):
        return [m for lvl, m in L.doctor(self.ws) if lvl in ("WARN", "INFO")]

    def test_fresh_workspace_has_no_upkeep_notes(self):
        self.assertEqual(L.knowledge_upkeep(self.ws, R), [])

    def test_references_to_replaced_retired_or_missing_decisions(self):
        write(self.ws / "proposals/2026-10-20-fridays.md", proposal("Reports go out on Fridays"))
        R.review(self.ws, "proposals/2026-10-20-fridays.md", "approve", "Sam", date="2026-10-20")
        old = R.current_decisions(self.ws)[0]
        write(self.ws / "workflows/report/CONTEXT.md", f"# Report\n\nDecisions that apply: `{old}`\n")
        write(self.ws / "knowledge/x.md", "# X\n\nSee `decisions/2026-01-01-nothing.md`.\n")
        self.assertFalse(any("replaced" in m for m in self.notes()))
        write(self.ws / "proposals/2026-10-21-mondays.md",
              proposal("Reports go out on Mondays", "replace", old, L.sha256(self.ws / old)))
        R.review(self.ws, "proposals/2026-10-21-mondays.md", "approve", "Sam", date="2026-10-21")
        notes = " | ".join(self.notes())
        self.assertIn(f"workflows/report/CONTEXT.md points to {old}, which was replaced; the rule now is "
                      f"decisions/2026-10-21-mondays.md", notes)
        self.assertIn("decisions/2026-01-01-nothing.md, which does not exist", notes)
        new = "decisions/2026-10-21-mondays.md"
        write(self.ws / "proposals/2026-10-22-stop.md", proposal("Stop reports", "retire", new, L.sha256(self.ws / new)))
        R.review(self.ws, "proposals/2026-10-22-stop.md", "approve", "Sam", date="2026-10-22")
        self.assertIn("which was retired", " | ".join(self.notes()))

    def test_duplicates_and_drawers(self):
        write(self.ws / "knowledge/a.md", "# Pricing rules\n\nOne.\n")
        write(self.ws / "knowledge/b.md", "# pricing  RULES\n\nTwo.\n")
        write(self.ws / "knowledge/c.md", "same text\n")
        write(self.ws / "knowledge/d.md", "same text\n")
        notes = " | ".join(self.notes())
        self.assertIn("knowledge/a.md and knowledge/b.md look like the same knowledge", notes)
        self.assertIn("knowledge/c.md and knowledge/d.md look like the same knowledge", notes)
        for i in range(L.DRAWER_AT):
            write(self.ws / f"knowledge/n{i}.md", f"# Note {i}\n")
        self.assertIn("in one folder; group files", " | ".join(self.notes()))

    def test_long_instructions(self):
        agents = self.ws / "AGENTS.md"
        write(agents, agents.read_text(encoding="utf-8") + "\n- extra rule\n" * (L.INSTRUCTION_GROWTH + 5))
        self.assertIn("AGENTS.md is about", " | ".join(self.notes()))
        self.assertIn("**Knowledge drawers.**", (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

"""The evidence summary: counts a person can show others, never content, names or titles."""
import subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def proposal(title):
    return (f"---\nstatus: proposed\nkind: new\ntarget: none\nevidence: e\nproposed_by: a\ndate: 2026-10-20\n---\n"
            f"\n# Proposal: {title}\n\n## Proposed future state\n\n> {title}.\n\n## Why and open questions\n\nt\n")


class TestEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def test_fresh_workspace_says_what_is_not_done(self):
        text = L.evidence(self.ws)
        self.assertTrue(text.startswith(L.EVIDENCE_MARK))
        self.assertIn("Not done yet", text)
        self.assertIn("Rules in force: 0", text)
        self.assertIn("Time or money saved: not measured", text)

    def test_counts_without_content_names_or_titles(self):
        write(self.ws / "proposals/2026-10-20-acme.md", proposal("Acme Corp invoices go to Jana Novak"))
        write(self.ws / "proposals/2026-10-21-other.md", proposal("Secret pricing for Globex"))
        R.review(self.ws, "proposals/2026-10-20-acme.md", "approve", "Jana Novak", date="2026-10-20")
        R.review(self.ws, "proposals/2026-10-21-other.md", "reject", "Jana Novak", date="2026-10-21")
        L.runs(self.ws, add="client-update")
        L.runs(self.ws, add="client-update")
        q = self.ws / "value-check/questions.md"
        write(q, "| # | Question | Before | After |\n| --- | --- | --- | --- |\n| 1 | Who signs off Acme? | made up | right |\n"
                 "| 2 | Who approves? | don't know | right |\n")
        write(self.ws / "value-check/log.md", "# Log\n\n- 2026-10-21 agent named the right file\n- 2026-10-22 ok\n")
        before = {p: p.read_bytes() for p in self.ws.rglob("*") if p.is_file()}
        text = L.evidence(self.ws)
        self.assertEqual({p: p.read_bytes() for p in self.ws.rglob("*") if p.is_file()}, before)
        for private in ("Acme", "Jana", "Globex", "client-update", "Who signs off"):
            self.assertNotIn(private, text)
        self.assertIn("| before | 0 | 0 | 1 | 1 |", text)
        self.assertIn("| after | 2 | 0 | 0 | 0 |", text)
        self.assertIn("Dated notes in the value check log: 2.", text)
        self.assertIn("Proposals: 1 approved, 1 rejected, 0 deferred, 0 waiting.", text)
        self.assertIn("Review record: intact, 2 entries.", text)
        self.assertIn("Kinds of repeated work counted: 1, 2 run(s) in total", text)
        self.assertIn("First recorded date: 2026-10-20.", text)

    def test_saved_outside_only_and_never_over_other_files(self):
        with self.assertRaises(L.Refusal):
            L.write_handbook(self.ws, self.ws / "e.md", L.evidence(self.ws), L.EVIDENCE_MARK, "evidence summary")
        handbook = Path(self.tmp.name) / "handbook.md"
        L.write_handbook(self.ws, handbook, L.handbook(self.ws))
        with self.assertRaises(L.Refusal):  # a handbook is not an evidence summary
            L.write_handbook(self.ws, handbook, L.evidence(self.ws), L.EVIDENCE_MARK, "evidence summary")
        r = subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "evidence", str(self.ws), "--out",
                            str(Path(self.tmp.name) / "evidence.md")], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Read it before you share it", r.stdout)

    def test_guide_and_skill(self):
        guide = (REPO / "docs/champions.md").read_text(encoding="utf-8")
        for audience in ("**CEO**", "**CTO**", "**Founder**"):
            self.assertIn(audience, guide)
        self.assertIn("Do not add numbers you did not measure", guide)
        self.assertTrue((self.ws / ".claude/skills/make-the-case/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()

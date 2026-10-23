"""The read-only 'what needs my attention' summary."""
import subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")


class TestStatus(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "student", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def test_fresh_workspace_lists_drafts_and_changes_nothing(self):
        before = snapshot(self.ws)
        text = L.status(self.ws)
        self.assertIn("Rules in force: 0 current decision(s)", text)
        self.assertIn("Read SYSTEM.md and change status: draft", text)
        self.assertNotIn("Last session's next step", text)
        self.assertEqual(snapshot(self.ws), before)

    def test_lists_pending_proposals_lessons_and_next_step(self):
        for f in ("SYSTEM.md", "PRINCIPLES.md"):
            p = self.ws / f
            write(p, p.read_text(encoding="utf-8").replace("status: draft", "status: approved", 1))
        write(self.ws / "proposals/2026-10-20-x.md",
              "---\nstatus: proposed\nkind: new\ntarget: none\nevidence: e\nproposed_by: a\ndate: 2026-10-20\n---\n"
              "\n# Proposal: Submit the report on Mondays\n\n## Proposed future state\n\n> Rule.\n\n"
              "## Why and open questions\n\nq\n")
        write(self.ws / "proposals/2026-10-01-done.md",
              "---\nstatus: rejected\nkind: new\ntarget: none\nevidence: e\nproposed_by: a\ndate: 2026-10-01\n---\n"
              "\n# Proposal: Old\n")
        L.add_module(self.ws, "staged-learning", apply=True)
        with open(self.ws / "lessons/inbox.md", "a", encoding="utf-8", newline="\n") as f:
            f.write("\n---lesson---\nLesson: keep it short\n---end---\n")
        write(self.ws / "handover/LATEST.md", "# Handover: latest\n\n- **One next step for you:** review the report proposal\n")
        text = L.status(self.ws)
        self.assertIn("Review proposals/2026-10-20-x.md (new rule): Submit the report on Mondays", text)
        self.assertIn("python3 tools/review.py review proposals/2026-10-20-x.md --outcome approve|reject|defer", text)
        self.assertNotIn("2026-10-01-done", text)
        self.assertIn("1 lesson suggestion(s)", text)
        self.assertNotIn("SYSTEM.md", text)
        self.assertIn("Last session's next step: review the report proposal", text)
        self.assertIn("Health: 0 error(s)", text)

    def test_next_step_written_as_a_section(self):
        write(self.ws / "handover/LATEST.md", "# Handover: latest\n\n## One next step for you\n\n- Review the draft\n")
        self.assertEqual(L.handover_next_step(self.ws), "Review the draft")

    def test_cli(self):
        r = subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "status", str(self.ws)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Waiting for you:", r.stdout)


if __name__ == "__main__":
    unittest.main()

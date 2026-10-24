"""Atlas, share withdrawal and the perspectives skill."""
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


class TestAtlas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "professional", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_workspace(self):
        text = L.atlas(self.ws)
        self.assertTrue(text.startswith(L.ATLAS_MARK))
        self.assertIn("## Rules in force (0)\n\nNone yet.", text)
        self.assertIn("## History (0)\n\nNone.", text)

    def test_links_history_and_stale_references(self):
        write(self.ws / "proposals/2026-10-20-fridays.md", proposal("Reports go out on Fridays"))
        R.review(self.ws, "proposals/2026-10-20-fridays.md", "approve", "Sam", date="2026-10-20")
        old = R.current_decisions(self.ws)[0]
        write(self.ws / "workflows/report/CONTEXT.md", f"# Report\n\nApplies: `{old}`\n")
        write(self.ws / "proposals/2026-10-21-mondays.md", proposal("Reports go out on Mondays", "replace", old, L.sha256(self.ws / old)))
        R.review(self.ws, "proposals/2026-10-21-mondays.md", "approve", "Sam", date="2026-10-21")
        new = "decisions/2026-10-21-mondays.md"
        write(self.ws / "projects/q4.md", f"# Q4\n\nSee `{new}`.\n")
        write(self.ws / "knowledge/archive/old.md", f"# Old\n\n`{old}`\n")  # archived files are left out
        text = L.atlas(self.ws)
        self.assertIn("```mermaid", text)
        self.assertIn(f"used by `projects/q4.md`", text)
        self.assertIn(f"`{old}` was replaced or amended by `{new}`", text)
        self.assertIn(f"`{old}` (history) is still named in `workflows/report/CONTEXT.md`", text)
        self.assertNotIn("knowledge/archive/old.md", text)

    def test_saved_outside_only(self):
        with self.assertRaises(L.Refusal):
            L.write_handbook(self.ws, self.ws / "atlas.md", L.atlas(self.ws), L.ATLAS_MARK, "atlas")
        L.write_handbook(self.ws, self.base / "atlas.md", L.atlas(self.ws), L.ATLAS_MARK, "atlas")


class TestWithdraw(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.org = L.init(base / "org", "manager", "en", team=True)
        self.me = L.init(base / "me", "employee", "en")
        L.link(self.me, self.org, "sales")
        write(self.me / "knowledge/tips.md", "# Tips\n\nAsk about the deadline first.\n")
        self.rel, _ = L.share(self.me, "knowledge/tips.md", apply=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_withdraw_while_waiting_only(self):
        self.assertIn("Withdrawn", L.withdraw_share(self.me, self.rel))
        self.assertFalse((self.org / self.rel).exists())
        self.assertTrue((self.me / "knowledge/tips.md").is_file())
        with self.assertRaises(L.Refusal):
            L.withdraw_share(self.me, self.rel)
        rel, _ = L.share(self.me, "knowledge/tips.md", apply=True)
        L.role_review(self.org, rel, "accept", "Kim Lead")
        with self.assertRaises(L.Refusal):
            L.withdraw_share(self.me, rel)

    def test_only_own_role_inbox(self):
        for rel in ("roles/other/inbox/x.md", "roles/sales/knowledge/tips.md", "SYSTEM.md", "roles/sales/inbox/../x.md"):
            with self.subTest(rel=rel), self.assertRaises(L.Refusal):
                L.withdraw_share(self.me, rel)

    def test_perspectives_skill_and_run_states(self):
        ws = L.init(Path(self.tmp.name) / "p", "student", "en")
        text = (ws / ".agents/skills/perspectives/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("never by a real person", text)
        verify = (REPO / "modules/careful-run/files/workflows/careful-run/05-verify/CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("'Finished' is not 'delivered'", verify)


if __name__ == "__main__":
    unittest.main()

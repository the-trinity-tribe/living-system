"""Agency view and delegation levels: delegations are ordinary proposals and decisions, never permissions."""
import datetime, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R

TODAY = datetime.date(2026, 10, 24)


class TestDelegation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "manager", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def approve_all(self):
        for p in sorted((self.ws / "proposals").glob("*.md")):
            if "status: proposed" in p.read_text(encoding="utf-8"):
                R.review(self.ws, f"proposals/{p.name}", "approve", "Ann")

    def test_a_delegation_is_a_proposal_until_approved(self):
        rel, text = L.delegate(self.ws, "weekly update drafts", "draft", "five drafts used unchanged", apply=True, today=TODAY)
        self.assertIn("> Delegation: weekly update drafts = draft.", text)
        self.assertEqual(L.delegations(self.ws), [])
        self.approve_all()
        [(work, level, rest, k, due)] = L.delegations(self.ws)
        self.assertEqual((work, level, due), ("weekly update drafts", "draft", False))

    def test_bounded_needs_scope_and_a_near_review_date(self):
        for kw in ({}, {"scope": "headings only"}, {"scope": "x", "review": "2026-10-01"},
                   {"scope": "x", "review": "2027-06-01"}, {"scope": "x", "review": "soon"}):
            with self.subTest(**kw), self.assertRaises(L.Refusal):
                L.delegate(self.ws, "tidy headings", "bounded", "e", today=TODAY, **kw)
        L.delegate(self.ws, "tidy headings", "bounded", "e", scope="headings in knowledge/", review="2026-11-30", today=TODAY)

    def test_always_approval_work_is_never_bounded(self):
        for work in ("send client emails", "publish the newsletter", "pay invoices", "delete old files",
                     "change rules", "sign contracts"):
            with self.subTest(work=work), self.assertRaises(L.Refusal):
                L.delegate(self.ws, work, "bounded", "e", scope="all", review="2026-11-30", today=TODAY)
            L.delegate(self.ws, work, "act-with-approval", "e", today=TODAY)  # this much is allowed
        with self.assertRaises(L.Refusal):  # a harmless name with a risky scope
            L.delegate(self.ws, "tidy files", "bounded", "e", scope="and delete duplicates", review="2026-11-30", today=TODAY)

    def test_bad_names_and_levels(self):
        for work, level in (("", "draft"), ("x" * 81, "draft"), ("a = b", "draft"), ("tidy", "everything")):
            with self.subTest(work=work[:10], level=level), self.assertRaises(L.Refusal):
                L.delegate(self.ws, work, level, "e", today=TODAY)

    def test_review_date_reached_shows_in_status_and_agency(self):
        L.delegate(self.ws, "tidy headings", "bounded", "e", scope="headings in knowledge/", review="2026-11-30",
                   apply=True, today=TODAY)
        self.approve_all()
        self.assertFalse(L.delegations(self.ws, today=TODAY)[0][4])
        self.assertTrue(L.delegations(self.ws, today=datetime.date(2026, 12, 1))[0][4])
        self.assertIn("Scope: headings in knowledge/.", L.agency(self.ws))

    def test_retiring_withdraws_it(self):
        L.delegate(self.ws, "weekly update drafts", "recommend", "e", apply=True, today=TODAY)
        self.approve_all()
        k = L.delegations(self.ws)[0][3]
        L.propose(self.ws, "retire", "Stop the weekly update delegation", "No longer needed.", "owner", target=k, apply=True)
        self.approve_all()
        self.assertEqual(L.delegations(self.ws), [])


class TestAgencyView(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_marks_what_is_enforced_and_what_is_not(self):
        ws = L.init(self.base / "ws", "manager", "en", team=True)
        text = L.agency(ws)
        self.assertIn("[enforced] Team workspace: review.py refuses an approval by whoever proposed the change.", text)
        self.assertIn("[enforced] The write guard runs in Claude Code and Codex", text)
        self.assertIn("Everything else: draft", text)
        self.assertIn("Not provided: login", text)
        (ws / ".claude/settings.json").unlink()
        (ws / ".codex/hooks.json").unlink()
        self.assertIn("[instruction] The write guard is not active here", L.agency(ws))

    def test_personal_workspace_view_and_command_line(self):
        ws = L.init(self.base / "me", "student", "en")
        self.assertIn("[instruction] Not a team workspace", L.agency(ws))
        r = subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "agency", str(ws)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("## 15. Agency and delegation", (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

"""Onboarding: a private reading path through company rules, role knowledge, workflows and own rules."""
import subprocess, sys, tempfile, unittest
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


class TestOnboard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.org = L.init(base / "org", "manager", "en", team=True)
        self.me = L.init(base / "me", "employee", "en")
        write(self.org / "proposals/2026-10-20-discounts.md", proposal("Discounts need the lead"))
        R.review(self.org, "proposals/2026-10-20-discounts.md", "approve", "Ali", date="2026-10-20")
        write(self.org / "roles/sales/knowledge/q4.md", "# Questions in Q4\n\nVolume discounts.\n")
        write(self.org / "roles/other/knowledge/x.md", "# Not for sales\n")
        L.add_module(self.org, "weekly-update", apply=True)
        write(self.me / "proposals/2026-10-20-mine.md", proposal("I answer within two days"))
        R.review(self.me, "proposals/2026-10-20-mine.md", "approve", "Sam", date="2026-10-20")

    def tearDown(self):
        self.tmp.cleanup()

    def ids(self):
        return [i for _, i, _ in L.onboarding_items(self.me)]

    def test_unlinked_path_has_only_own_items(self):
        self.assertEqual(self.ids(), ["here:decisions/2026-10-20-mine.md"])

    def test_company_items_come_first_and_only_for_the_role(self):
        L.link(self.me, self.org, "sales")
        self.assertEqual(self.ids(), ["company:decisions/2026-10-20-discounts.md", "company:roles/sales/knowledge/q4.md",
                                      "company:workflows/weekly-update/CONTEXT.md", "here:decisions/2026-10-20-mine.md"])

    def test_gradual_ticks_kept_and_changed_rules_come_back(self):
        L.link(self.me, self.org, "sales")
        nxt, done, total, _ = L.onboard(self.me, per=2)
        self.assertEqual((len(nxt), done, total), (2, 0, 4))
        L.onboard(self.me, done="decisions/2026-10-20-discounts.md")
        nxt, done, total, _ = L.onboard(self.me)
        self.assertEqual((done, total), (1, 4))
        self.assertIn("[x] Discounts need the lead", (self.me / L.ONBOARD_FILE).read_text(encoding="utf-8"))
        old = R.current_decisions(self.org)[0]
        write(self.org / "proposals/2026-10-21-discounts-ten.md",
              proposal("Discounts over ten percent need the lead", "replace", old, L.sha256(self.org / old)))
        R.review(self.org, "proposals/2026-10-21-discounts-ten.md", "approve", "Ali", date="2026-10-21")
        nxt, done, total, _ = L.onboard(self.me)
        self.assertEqual((done, total), (0, 4))  # the replaced rule left the path; the new one waits
        self.assertIn("Discounts over ten percent", nxt[0][2])

    def test_refusals_and_no_needless_writes(self):
        L.onboard(self.me)
        path = self.me / L.ONBOARD_FILE
        before = path.stat().st_mtime_ns
        L.onboard(self.me)
        self.assertEqual(path.stat().st_mtime_ns, before)
        for kw in ({"done": "decisions/unknown.md"}, {"per": 0}):
            with self.subTest(**kw), self.assertRaises(L.Refusal):
                L.onboard(self.me, **kw)

    def test_status_and_command_line(self):
        L.onboard(self.me)
        self.assertIn("Onboarding: 1 of 1 item(s) still to read", L.status(self.me))
        r = subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "onboard", str(self.me), "--done",
                            "here:decisions/2026-10-20-mine.md"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("all 1 item(s) done", r.stdout)
        self.assertNotIn("Onboarding:", L.status(self.me))

    def test_rules_and_skill(self):
        self.assertIn("**Onboarding.**", (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8"))
        self.assertTrue((self.me / ".agents/skills/onboarding/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()

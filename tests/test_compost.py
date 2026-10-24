"""Knowledge metabolism: confidence notes and composting into the archive."""
import datetime, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class TestCompost(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")
        write(self.ws / "knowledge/prices-2025.md", "---\nlast_verified: 2025-01-01\n---\n\n# Prices 2025\n\nOld list.\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_plan_then_move_with_date_and_reason(self):
        dest, text = L.compost(self.ws, "knowledge/prices-2025.md", "replaced by the 2026 list",
                               today=datetime.date(2026, 10, 24))
        self.assertEqual(dest, "knowledge/archive/prices-2025.md")
        self.assertTrue((self.ws / "knowledge/prices-2025.md").is_file())  # plan only
        self.assertIn("archived_on: 2026-10-24\narchive_reason: replaced by the 2026 list\n", text)
        L.compost(self.ws, "knowledge/prices-2025.md", "replaced by the 2026 list", apply=True)
        self.assertFalse((self.ws / "knowledge/prices-2025.md").exists())
        self.assertIn("Old list.", (self.ws / dest).read_text(encoding="utf-8"))

    def test_archived_files_leave_upkeep_freshness_and_sharing(self):
        before = [m for lvl, m in L.doctor(self.ws) if "prices-2025" in m]
        self.assertTrue(before)  # old last_verified is flagged while in use
        L.compost(self.ws, "knowledge/prices-2025.md", "outdated", apply=True)
        self.assertFalse([m for lvl, m in L.doctor(self.ws) if "prices-2025" in m])
        org = L.init(Path(self.tmp.name) / "org", "manager", "en", team=True)
        L.link(self.ws, org, "sales")
        with self.assertRaises(L.Refusal):
            L.share(self.ws, "knowledge/archive/prices-2025.md")

    def test_refusals(self):
        write(self.ws / "knowledge/archive/x.md", "# X\n")
        for rel, reason in (("knowledge/archive/x.md", "r"), ("knowledge/README.md", "r"), ("projects/a.md", "r"),
                            ("knowledge/missing.md", "r"), ("knowledge/../SYSTEM.md", "r"), ("knowledge/prices-2025.md", ""),
                            ("knowledge/prices-2025.md", "x" * 201)):
            with self.subTest(rel=rel, reason=reason[:5]), self.assertRaises(L.Refusal):
                L.compost(self.ws, rel, reason)
        write(self.ws / "knowledge/archive/prices-2025.md", "# Already\n")
        with self.assertRaises(L.Refusal):
            L.compost(self.ws, "knowledge/prices-2025.md", "dup", apply=True)
        self.assertTrue((self.ws / "knowledge/prices-2025.md").is_file())

    def test_confidence_notes(self):
        write(self.ws / "knowledge/rumour.md", "---\nconfidence: low\n---\n\n# Rumour\n")
        write(self.ws / "knowledge/odd.md", "---\nconfidence: maybe\n---\n\n# Odd\n")
        write(self.ws / "knowledge/body.md", "---\nlast_verified: 2026-10-01\n---\n\n# Body\n\nconfidence: low\n")
        notes = {lvl + " " + m for lvl, m in L.knowledge_upkeep(self.ws, R)}
        self.assertTrue(any(n.startswith("INFO knowledge/rumour.md is marked low confidence") for n in notes))
        self.assertTrue(any(n.startswith("WARN knowledge/odd.md: confidence 'maybe'") for n in notes))
        self.assertFalse(any("body.md" in n for n in notes))  # only the front matter counts

    def test_command_line(self):
        r = subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "compost", str(self.ws),
                            "knowledge/prices-2025.md", "--reason", "outdated"], capture_output=True, text=True, encoding="utf-8")
        self.assertIn("Nothing was changed", r.stdout)


if __name__ == "__main__":
    unittest.main()

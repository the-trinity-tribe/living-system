"""Parked ideas: written down without switching task, listed, ticked off."""
import datetime, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


class TestPark(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "employee", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def test_park_list_and_tick_off(self):
        self.assertEqual(L.park(self.ws), ([], ""))
        self.assertFalse((self.ws / L.PARKED_FILE).exists())  # listing writes nothing
        L.park(self.ws, "A newsletter   for clients", today=datetime.date(2026, 10, 24))
        L.park(self.ws, "Try the second-check module")
        ideas, _ = L.park(self.ws)
        self.assertEqual(ideas[0], ("2026-10-24", "A newsletter for clients"))
        ideas, message = L.park(self.ws, done=1)
        self.assertIn("A newsletter for clients", message)
        self.assertEqual([i for _, i in ideas], ["Try the second-check module"])
        self.assertIn("- [x] 2026-10-24 A newsletter for clients", (self.ws / L.PARKED_FILE).read_text(encoding="utf-8"))
        self.assertIn("Parked ideas: 1", L.status(self.ws))

    def test_refusals(self):
        for kw in ({"idea": ""}, {"idea": "x" * 301}, {"idea": "wifi password: Summer2026x"}, {"done": 1}):
            with self.subTest(**kw), self.assertRaises(L.Refusal):
                L.park(self.ws, **kw)

    def test_command_line_and_skills(self):
        run = lambda *a: subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "park", str(self.ws), *a],
                                        capture_output=True, text=True, encoding="utf-8")
        self.assertIn("Parked. Carry on", run("Ask about a shared calendar").stdout)
        self.assertIn("1. ", run().stdout)
        for skill in ("tend", "idea-check"):
            self.assertTrue((self.ws / ".claude/skills" / skill / "SKILL.md").is_file())
        self.assertIn("**Parking and tending.**", (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

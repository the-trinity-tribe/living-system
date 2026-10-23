"""The decision history: what is in force and what changed each older decision."""
import subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

R = L.review_tool()


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "manager", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def step(self, kind, title, rule, date, target=None):
        rel, _ = L.propose(self.ws, kind, title, rule, "test", target=target, date=date, apply=True)
        return R.review(self.ws, rel, "approve", "Owner", date=date)[1]

    def test_full_chain(self):
        self.assertEqual(R.history(self.ws), [])
        self.assertEqual(R.format_history([]), "No decisions yet.")
        first = self.step("new", "Only I send to clients", "Only I send things to clients.", "2026-10-01")
        amended = self.step("exception", "Alex sends rotas", "Alex may send routine rotas.", "2026-10-02", first)
        replaced = self.step("replace", "Team sends updates", "Anyone on the team may send updates.", "2026-10-03", amended)
        retired = self.step("retire", "No client rule", "We stopped client work.", "2026-10-04", replaced)
        states = {k: state for k, _, _, _, state in R.history(self.ws)}
        self.assertEqual(states[first], f"amended by {amended} on 2026-10-02")
        self.assertEqual(states[amended], f"replaced by {replaced} on 2026-10-03")
        self.assertEqual(states[replaced], f"retired by {retired} on 2026-10-04")
        self.assertEqual(states[retired], f"retirement record for {replaced}")
        self.assertEqual([k for k, *_ in R.history(self.ws)], [first, amended, replaced, retired])

    def test_cli_and_demo(self):
        r = subprocess.run([sys.executable, "-B", str(REPO / "tools/review.py"), "--root", str(REPO / "demo/moss-and-circuit"),
                            "history"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("amended by decisions/2026-10-07-leo-signs-off-riverside-rota-updates.md", r.stdout)
        self.assertIn("in force", r.stdout)
        self.assertIn("attribution, not verified", r.stdout)


if __name__ == "__main__":
    unittest.main()

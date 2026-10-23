"""The Third-Run counter: a visible count of repeated work, with the human's decision."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


class TestRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, name="weekly-update"):
        return L.runs(self.ws, add=name, date="2026-10-24")

    def test_nothing_before_the_third_run_then_a_decision_is_due(self):
        for n in (1, 2):
            work, msg = self.add()
            self.assertIn("Nothing else happens before the third run", msg)
            self.assertNotIn("weekly-update", L.status(self.ws))
        work, msg = self.add()
        self.assertEqual(work["weekly-update"]["count"], 3)
        self.assertIn("time to decide", msg)
        self.assertIn("'weekly-update' has come up 3 times", L.status(self.ws))

    def test_decisions_manual_and_later(self):
        for _ in range(3):
            self.add()
        L.runs(self.ws, decide="weekly-update", decision="manual")
        self.assertNotIn("weekly-update", L.status(self.ws))
        self.assertIn("decision on record: manual", self.add()[1])
        L.runs(self.ws, decide="weekly-update", decision="later", after=2)
        self.assertIn("asked again at run 6", self.add()[1])
        self.assertIn("time to decide", self.add()[1])

    def test_only_short_names_are_stored_and_forget_removes_them(self):
        for bad in ("Acme Client", "weekly update", "../x", ""):
            with self.subTest(name=bad):
                with self.assertRaises(L.Refusal):
                    L.runs(self.ws, add=bad or "-")
        self.add("call-notes")
        data = json.loads((self.ws / L.RUNS_FILE).read_text(encoding="utf-8"))
        self.assertEqual(set(data["work"]["call-notes"]), {"count", "first", "last", "decision"})
        self.assertIn("never content", data["_about"])
        L.runs(self.ws, forget="call-notes")
        self.assertEqual(L.runs(self.ws)[0], {})

    def test_a_new_name_lists_the_names_already_counted(self):
        self.add("weekly-update")
        msg = self.add("client-update")[1]
        self.assertIn("Already counted: weekly-update", msg)
        self.assertIn("--forget client-update", msg)
        self.assertNotIn("Already counted", self.add("client-update")[1])

    def test_refusals(self):
        with self.assertRaises(L.Refusal):
            L.runs(self.ws, decide="never-counted", decision="manual")
        self.add()
        with self.assertRaises(L.Refusal):
            L.runs(self.ws, decide="weekly-update", decision="maybe")
        with self.assertRaises(L.Refusal):
            L.runs(self.ws, forget="never-counted")
        (self.ws / L.RUNS_FILE).write_text("{", encoding="utf-8")
        with self.assertRaises(L.Refusal):
            self.add()
        self.assertIn("is damaged", L.status(self.ws))

    def test_counts_survive_upgrade_and_do_not_bother_doctor(self):
        for _ in range(3):
            self.add()
        before = (self.ws / L.RUNS_FILE).read_bytes()
        L.upgrade(self.ws, apply=True)
        self.assertEqual((self.ws / L.RUNS_FILE).read_bytes(), before)
        self.assertFalse([m for _, m in L.doctor(self.ws) if "runs" in m])

    def test_cli(self):
        run = lambda *a: subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "runs", str(self.ws), *a],
                                        capture_output=True, text=True)
        self.assertIn("run 1", run("--add", "newsletter").stdout)
        self.assertIn("newsletter: 1 run(s)", run().stdout)
        self.assertIn("decision 'later' recorded", run("--decide", "newsletter", "later").stdout)
        self.assertEqual(run("--add", "Bad Name").returncode, 2)



class TestRunsReview4(unittest.TestCase):
    def test_malformed_entries_are_refused_and_status_survives(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = L.init(Path(tmp) / "ws", "student", "en")
            for bad in ('{"work":{"weekly-update":{}}}', '{"work":{"weekly-update":{"count":"3","first":"","last":"","decision":null}}}',
                        '{"work":{"Bad Name":{"count":1,"first":"","last":"","decision":null}}}', '[]'):
                with self.subTest(content=bad):
                    (ws / L.RUNS_FILE).write_text(bad, encoding="utf-8")
                    with self.assertRaises(L.Refusal):
                        L.runs(ws)
                    self.assertIn("unexpected structure" if bad != "[]" else "unexpected structure", L.status(ws))

if __name__ == "__main__":
    unittest.main()

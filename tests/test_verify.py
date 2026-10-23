"""The review record: every review is fingerprinted and chained, so later changes show up."""
import json, os, subprocess, sys, tempfile, unittest
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


class TestRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "manager", "en")
        write(self.ws / "proposals/2026-10-20-fridays.md", proposal("Reports go out on Fridays"))
        write(self.ws / "proposals/2026-10-20-calls.md", proposal("Calls are recorded"))
        R.review(self.ws, "proposals/2026-10-20-fridays.md", "approve", "Ann", date="2026-10-21")
        R.review(self.ws, "proposals/2026-10-20-calls.md", "reject", "Ann", date="2026-10-21")
        self.decision = self.ws / "decisions/2026-10-21-fridays.md"

    def tearDown(self):
        self.tmp.cleanup()

    def levels(self):
        return [(lvl, msg.split(":")[0]) for lvl, msg in R.verify(self.ws)]

    def test_each_review_adds_one_chained_line(self):
        lines = R.record_lines(self.ws)
        self.assertEqual(len(lines), 2)
        first, second = map(json.loads, lines)
        self.assertEqual((first["n"], first["outcome"], first["prev"]), (1, "approve", "start"))
        self.assertEqual(set(first["files"]), {"decisions/2026-10-21-fridays.md", "proposals/2026-10-20-fridays.md"})
        self.assertEqual(second["prev"], R.text_sha(lines[0]))
        self.assertEqual(R.verify(self.ws), [])
        self.assertIn("Review record intact: 2 entries", R.format_verify([], self.ws))

    def test_a_changed_or_deleted_decision_is_reported(self):
        write(self.decision, self.decision.read_text(encoding="utf-8").replace("Fridays.", "Mondays."))
        self.assertIn(("ERROR", "decisions/2026-10-21-fridays.md"), self.levels())
        self.decision.unlink()
        self.assertTrue(any("is missing" in m for _, m in R.verify(self.ws)))

    def test_windows_line_endings_are_not_a_change(self):
        data = self.decision.read_bytes().replace(b"\n", b"\r\n")
        self.decision.write_bytes(data)
        self.assertEqual(R.verify(self.ws), [])

    def test_a_reviewed_proposal_set_back_by_hand_is_reported(self):
        p = self.ws / "proposals/2026-10-20-calls.md"
        write(p, p.read_text(encoding="utf-8").replace("status: rejected", "status: proposed"))
        self.assertIn(("ERROR", "proposals/2026-10-20-calls.md"), self.levels())

    def test_a_decision_written_by_hand_is_a_warning(self):
        write(self.ws / "decisions/2026-10-22-by-hand.md", "---\nstatus: approved\n---\n\n# By hand\n\n## Rule\n\nR.\n")
        self.assertEqual(self.levels(), [("WARN", "decisions/2026-10-22-by-hand.md")])

    def test_editing_the_record_itself_is_reported(self):
        path = self.ws / R.RECORD
        lines = path.read_text(encoding="utf-8").splitlines()
        cases = {"edited": [lines[0].replace("Ann", "Bob"), lines[1]], "removed": [lines[1]],
                 "added": lines + [lines[1]], "not json": lines + ["{oops"]}
        for name, new in cases.items():
            with self.subTest(case=name):
                write(path, "\n".join(new) + "\n")
                [(level, message)] = R.verify(self.ws)
                self.assertEqual(level, "ERROR")
                self.assertIn("edited, removed or added by hand", message)

    def test_a_refused_review_adds_nothing_to_the_record(self):
        before = (self.ws / R.RECORD).read_bytes()
        with self.assertRaises(R.Refusal):
            R.review(self.ws, "proposals/2026-10-20-calls.md", "approve", "Ann")
        self.assertEqual((self.ws / R.RECORD).read_bytes(), before)

    @unittest.skipIf(os.name == "nt", "links need extra rights on Windows")
    def test_a_linked_record_is_refused(self):
        outside = Path(self.tmp.name) / "elsewhere.jsonl"
        (self.ws / R.RECORD).rename(outside)
        (self.ws / R.RECORD).symlink_to(outside)
        write(self.ws / "proposals/2026-10-23-x.md", proposal("X"))
        with self.assertRaises(R.Refusal):
            R.review(self.ws, "proposals/2026-10-23-x.md", "approve", "Ann")
        self.assertEqual(R.verify(self.ws)[0][0], "ERROR")

    def test_doctor_shows_changes_as_errors(self):
        write(self.decision, self.decision.read_text(encoding="utf-8") + "\nmore\n")
        self.assertTrue(any(lvl == "ERROR" and "changed after it was recorded" in m for lvl, m in L.doctor(self.ws)))


class TestStart(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "manager", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_record_is_a_note_and_start_covers_what_exists(self):
        write(self.ws / "decisions/2026-10-01-old.md", "---\nstatus: approved\n---\n\n# Old\n\n## Rule\n\nR.\n")
        write(self.ws / "proposals/2026-10-02-open.md", proposal("Open"))
        self.assertEqual(R.verify(self.ws)[0][0], "INFO")
        self.assertEqual(R.start_record(self.ws, "Ann"), 1)  # the open proposal is not covered: nothing was decided
        self.assertEqual(R.verify(self.ws), [])
        with self.assertRaises(R.Refusal):
            R.start_record(self.ws, "Ann")

    def test_command_line(self):
        run = lambda *a: subprocess.run([sys.executable, "-B", str(self.ws / "tools/review.py"), *a],
                                        capture_output=True, text=True, encoding="utf-8", cwd=self.ws)
        self.assertEqual(run("verify").returncode, 0)
        self.assertEqual(R.verify(self.ws), [])  # nothing decided yet: nothing to report
        self.assertEqual(run("verify", "--start").returncode, 2)  # --by is required
        started = run("verify", "--start", "--by", "Ann")
        self.assertEqual(started.returncode, 0, started.stderr)
        self.assertIn("Started decisions/review-record.jsonl", started.stdout)
        write(self.ws / "decisions/2026-10-01-x.md", "---\nstatus: approved\n---\n\n# X\n\n## Rule\n\nR.\n")
        self.assertEqual(run("verify").returncode, 0)  # a warning, not an error
        self.assertIn("WARN", run("verify").stdout)


if __name__ == "__main__":
    unittest.main()

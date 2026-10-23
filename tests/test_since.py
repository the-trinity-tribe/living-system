"""The read-only 'what changed while I was away' catch-up."""
import datetime, os, subprocess, sys, tempfile, time, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R

TODAY = datetime.date.today()


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def age(path, days):
    t = time.time() - days * 86400
    os.utime(path, (t, t))


def proposal(title, date, kind="new", target="none", extra=""):
    return (f"---\nstatus: proposed\nkind: {kind}\ntarget: {target}\n{extra}evidence: e\nproposed_by: a\ndate: {date}\n---\n"
            f"\n# Proposal: {title}\n\n## Proposed future state\n\n> {title}.\n\n## Why and open questions\n\nt\n")


class TestSince(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "manager", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def back(self, days):
        return (TODAY - datetime.timedelta(days=days)).isoformat()

    def test_fresh_workspace_reports_no_changes_and_writes_nothing(self):
        before = snapshot(self.ws)
        text = L.since(self.ws, self.back(1))
        self.assertIn("Rules: no changes.", text)
        self.assertIn("Proposals: no changes.", text)
        self.assertNotIn("Other files changed", text)  # files as installed are not changes
        self.assertEqual(snapshot(self.ws), before)

    def test_new_replaced_and_retired_rules_come_first(self):
        old = self.back(30)
        write(self.ws / "proposals/2026-01-01-aa.md", proposal("Reports go out on Fridays", old))
        R.review(self.ws, "proposals/2026-01-01-aa.md", "approve", "Ann", date=old)
        first = R.current_decisions(self.ws)[0]
        sha = L.sha256(self.ws / first)
        write(self.ws / "proposals/2026-01-01-bb.md", proposal("Reports go out on Mondays", self.back(2), "replace", first,
                                                   f"target_sha256: {sha}\n"))
        R.review(self.ws, "proposals/2026-01-01-bb.md", "approve", "Ben", date=self.back(2))
        write(self.ws / "proposals/2026-01-01-cc.md", proposal("Calls are recorded", self.back(1)))
        R.review(self.ws, "proposals/2026-01-01-cc.md", "approve", "Ben", date=self.back(1))
        third = [k for k in R.current_decisions(self.ws) if k.endswith("-cc.md")][0]
        write(self.ws / "proposals/2026-01-01-dd.md", proposal("Calls are no longer recorded", TODAY.isoformat(), "retire", third,
                                                   f"target_sha256: {L.sha256(self.ws / third)}\n"))
        R.review(self.ws, "proposals/2026-01-01-dd.md", "approve", "Ben")
        text = L.since(self.ws, self.back(3))
        self.assertLess(text.index("Rules (read these first):"), text.index("Proposals:"))
        self.assertIn("Replaced: Reports go out on Fridays", text)
        self.assertIn("New rule: Calls are recorded", text)
        self.assertIn("Retired: Calls are recorded", text)
        self.assertNotIn("New rule: Reports go out on Fridays", text)  # approved before the date
        self.assertIn("Next: read the changed rules first", text)

    def test_proposals_reviewed_or_waiting(self):
        write(self.ws / "proposals/2026-01-01-old.md", proposal("Old idea", self.back(40)))
        R.review(self.ws, "proposals/2026-01-01-old.md", "reject", "Ann", date=self.back(2))
        write(self.ws / "proposals/2026-01-01-new.md", proposal("New idea", self.back(1)))
        write(self.ws / "proposals/2026-01-01-ancient.md", proposal("Ancient idea", self.back(40)))
        text = L.since(self.ws, self.back(5))
        self.assertIn("rejected on", text)
        self.assertIn("Old idea", text)
        self.assertIn("new, waits for review: New idea", text)
        self.assertNotIn("Ancient idea", text)

    def test_handover_runs_and_other_files(self):
        write(self.ws / "handover/LATEST.md", "# Handover\n\n**Next step:** call the printer\n")
        L.runs(self.ws, add="weekly-update")
        write(self.ws / "projects/alpha.md", "# Alpha\n")
        write(self.ws / "projects/beta.md", "# Beta\n")
        age(self.ws / "projects/beta.md", 10)
        text = L.since(self.ws, self.back(3))
        self.assertIn("next step: call the printer", text)
        self.assertIn("repeated work 'weekly-update': 1 run(s)", text)
        self.assertIn("projects/alpha.md", text)
        self.assertNotIn("projects/beta.md", text)

    def test_edited_system_file_is_a_rule_change(self):
        p = self.ws / "SYSTEM.md"
        write(p, p.read_text(encoding="utf-8") + "\nA new line.\n")
        self.assertIn("SYSTEM.md was edited", L.since(self.ws, self.back(1)))

    def test_long_lists_are_cut(self):
        for i in range(L.SINCE_SHOWN + 3):
            write(self.ws / f"projects/p{i}.md", "x\n")
        self.assertIn("and 3 more", L.since(self.ws, self.back(1)))

    def test_bad_dates_are_refused(self):
        for bad in ("yesterday", "2026-13-01", (TODAY + datetime.timedelta(days=1)).isoformat()):
            with self.subTest(date=bad), self.assertRaises(L.Refusal):
                L.since(self.ws, bad)

    def test_command_line_days_and_refusal(self):
        run = lambda *a: subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "since", str(self.ws), *a],
                                        capture_output=True, text=True, encoding="utf-8")
        ok = run("--days", "7")
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn(f"since {self.back(7)}", ok.stdout)
        self.assertEqual(run("--days", "-1").returncode, 2)
        self.assertNotEqual(run().returncode, 0)


if __name__ == "__main__":
    unittest.main()

"""The review loop: rhythm and mode settings, the due line, the once-a-day nudge, and approvers."""
import datetime, json, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

D = datetime.date


def profile(ws):
    return json.loads((ws / ".living/profile.json").read_text(encoding="utf-8"))


def tree(ws):
    return {p.relative_to(ws).as_posix(): p.read_bytes() for p in sorted(ws.rglob("*")) if p.is_file()}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def propose(self, title="Only I send things to clients"):
        L.propose(self.ws, "new", title, "Nothing goes to a client without my OK.", "setup answer", apply=True,
                  date=self.day)
        return sorted((self.ws / "proposals").glob("*.md"))[-1]

    day = D(2026, 10, 1)


class TestSettings(Base):
    def test_new_workspace_defaults_to_weekly_batch(self):
        p = profile(self.ws)
        self.assertEqual((p["review_every"], p["review_mode"]), ("weekly", "batch"))
        self.assertRegex(p["review_set_on"], r"^\d{4}-\d{2}-\d{2}$")

    def test_init_flags_and_refusals(self):
        ws = L.init(Path(self.tmp.name) / "b", "student", "en", review_every="10", review_mode="ask-now")
        self.assertEqual((profile(ws)["review_every"], profile(ws)["review_mode"]), (10, "ask-now"))
        ws = L.init(Path(self.tmp.name) / "c", "student", "en", review_every="off")
        self.assertEqual(profile(ws)["review_every"], "off")
        for bad in ({"review_every": "sometimes"}, {"review_every": "0"}, {"review_every": "400"},
                    {"review_mode": "whenever"}):
            with self.subTest(**bad), self.assertRaises(L.Refusal):
                L.init(Path(self.tmp.name) / "d", "student", "en", **bad)
            self.assertFalse((Path(self.tmp.name) / "d").exists())  # nothing built after a refusal

    def test_review_rhythm_shows_and_sets_only_the_settings_file(self):
        before = tree(self.ws)
        self.assertIn("weekly", L.review_rhythm(self.ws))
        self.assertEqual(tree(self.ws), before)  # showing writes nothing
        message = L.review_rhythm(self.ws, every="monthly", mode="ask-now", today=D(2026, 10, 2))
        self.assertIn("Saved", message)
        after = tree(self.ws)
        self.assertEqual([k for k in after if after[k] != before.get(k)], [".living/profile.json"])
        p = profile(self.ws)
        self.assertEqual((p["review_every"], p["review_mode"], p["review_set_on"]), ("monthly", "ask-now", "2026-10-02"))
        with self.assertRaises(L.Refusal):
            L.review_rhythm(self.ws, every="soon")
        self.assertEqual(tree(self.ws), after)

    def test_damaged_settings_are_refused(self):
        (self.ws / ".living/profile.json").write_text("{not json", encoding="utf-8")
        for call in (lambda: L.review_rhythm(self.ws, every="weekly"), lambda: L.reviewed(self.ws),
                     lambda: L.nudge(self.ws)):
            with self.assertRaises(L.Refusal):
                call()


class TestDue(Base):
    def setUp(self):
        super().setUp()
        L.review_rhythm(self.ws, every="weekly", today=self.day)

    def test_quiet_when_nothing_waits(self):
        self.assertIsNone(L.review_due(self.ws, today=D(2027, 1, 1)))
        self.assertEqual(L.nudge(self.ws, today=D(2027, 1, 1)), "")
        self.assertNotIn("Review is due", L.status(self.ws))

    def test_quiet_before_the_rhythm_has_passed_then_due(self):
        self.propose()
        self.assertIsNone(L.review_due(self.ws, today=D(2026, 10, 7)))  # 6 days after the rhythm was set
        waiting, last, every = L.review_due(self.ws, today=D(2026, 10, 8))
        self.assertEqual((waiting, last, every), (1, self.day, "weekly"))
        self.assertIn("Review is due: 1 item(s) waiting, last looked over 2026-10-01 (your rhythm: weekly)",
                      L.due_line((waiting, last, every)))

    def test_status_shows_the_due_line_only_when_due(self):
        self.propose()
        L.review_rhythm(self.ws, every="weekly")  # set today, so not due today
        self.assertNotIn("Review is due", L.status(self.ws))
        p = profile(self.ws)
        p["review_set_on"] = "2020-01-01"
        (self.ws / ".living/profile.json").write_text(json.dumps(p), encoding="utf-8")
        self.assertIn("Review is due: 1 item(s) waiting", L.status(self.ws))

    def test_rhythm_off_or_unset_is_silent(self):
        self.propose()
        L.review_rhythm(self.ws, every="off")
        self.assertIsNone(L.review_due(self.ws, today=D(2030, 1, 1)))
        p = profile(self.ws)
        del p["review_every"]
        (self.ws / ".living/profile.json").write_text(json.dumps(p), encoding="utf-8")  # an older workspace
        self.assertIsNone(L.review_due(self.ws, today=D(2030, 1, 1)))
        self.assertIn("not set", L.review_rhythm(self.ws))

    def test_reviewed_resets_the_clock(self):
        self.propose()
        self.assertIsNotNone(L.review_due(self.ws, today=D(2026, 10, 20)))
        self.assertIn("Next review is due from 2026-10-27", L.reviewed(self.ws, today=D(2026, 10, 20)))
        self.assertIsNone(L.review_due(self.ws, today=D(2026, 10, 26)))
        self.assertIsNotNone(L.review_due(self.ws, today=D(2026, 10, 27)))

    def test_a_recorded_review_counts_as_a_look(self):
        first = self.propose("First rule")
        L.propose(self.ws, "new", "Second rule", "Nothing is sent on Fridays.", "setup answer", apply=True,
                  date=self.day)
        subprocess.run([sys.executable, "-B", str(self.ws / "tools/review.py"), "--root", str(self.ws), "review",
                        f"proposals/{first.name}", "--outcome", "defer", "--by", "Me", "--date", "2026-10-15"],
                       check=True, capture_output=True)
        self.assertEqual(L.last_review_date(self.ws, profile(self.ws)), D(2026, 10, 15))
        self.assertIsNone(L.review_due(self.ws, today=D(2026, 10, 21)))
        self.assertIsNotNone(L.review_due(self.ws, today=D(2026, 10, 22)))

    def test_other_waiting_items_count(self):
        (self.ws / "knowledge").mkdir(exist_ok=True)
        (self.ws / "knowledge/inbox.md").write_text("---knowledge---\nx\n---knowledge---\ny\n", encoding="utf-8")
        self.assertEqual(L.review_waiting(self.ws), 2)


class TestNudge(Base):
    def setUp(self):
        super().setUp()
        L.review_rhythm(self.ws, every="daily", today=self.day)
        self.propose()

    def test_says_it_once_per_day_and_changes_nothing_else(self):
        before = tree(self.ws)
        line = L.nudge(self.ws, today=D(2026, 10, 3))
        self.assertTrue(line.startswith("Review is due"))
        after = tree(self.ws)
        self.assertEqual([k for k in after if after[k] != before.get(k)], [".living/profile.json"])
        self.assertEqual(profile(self.ws)["nudged_on"], "2026-10-03")
        self.assertEqual(L.nudge(self.ws, today=D(2026, 10, 3)), "")  # same day: silent
        self.assertTrue(L.nudge(self.ws, today=D(2026, 10, 4)))  # next day: again, still due
        self.assertIn("status: proposed", next((self.ws / "proposals").glob("*.md")).read_text(encoding="utf-8"))

    def test_not_due_writes_nothing(self):
        L.reviewed(self.ws, today=D(2026, 10, 3))
        before = tree(self.ws)
        self.assertEqual(L.nudge(self.ws, today=D(2026, 10, 3)), "")
        self.assertEqual(tree(self.ws), before)

    def test_never_reviews_anything(self):
        L.nudge(self.ws, today=D(2026, 10, 3))
        self.assertEqual(list((self.ws / "decisions").glob("*.md")), [])
        self.assertFalse((self.ws / "decisions/review-record.jsonl").exists())

    def test_command_line(self):
        run = lambda *a: subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), *a, str(self.ws)],
                                        capture_output=True, text=True, encoding="utf-8")
        out = run("nudge")
        self.assertEqual(out.returncode, 0)
        self.assertIn("Review is due", out.stdout)
        self.assertEqual(run("nudge").stdout, "")
        self.assertIn("Noted: you looked over", run("reviewed").stdout)
        self.assertIn("Review rhythm: daily", run("review-rhythm").stdout)


class TestApprovers(Base):
    def approve(self, rule, title):
        L.propose(self.ws, "new", title, rule, "setup answer", apply=True, date=self.day)
        proposal = sorted((self.ws / "proposals").glob("*.md"))[-1]
        subprocess.run([sys.executable, "-B", str(self.ws / "tools/review.py"), "--root", str(self.ws), "review",
                        f"proposals/{proposal.name}", "--outcome", "approve", "--by", "Owner", "--date", "2026-10-02"],
                       check=True, capture_output=True)

    def test_owner_only_until_a_decision_names_others(self):
        self.assertEqual(L.approvers(self.ws), [])
        self.assertIn("only the owner", L.agency(self.ws))
        self.assertNotIn("Approvers (approved", L.status(self.ws))

    def test_a_proposal_does_not_grant_approval_rights_only_an_approved_decision_does(self):
        L.propose(self.ws, "new", "Approvers: Alex", "Approvers: Alex may approve decisions about client updates.",
                  "setup answer", apply=True, date=self.day)
        self.assertEqual(L.approvers(self.ws), [])
        self.approve("Approvers: Alex may approve decisions about client updates.", "Approvers: Alex for client updates")
        found = L.approvers(self.ws)
        self.assertEqual(len(found), 1)
        self.assertIn("Alex may approve decisions about client updates", found[0][0])
        self.assertIn("Approvers (approved decision", L.status(self.ws))
        agency = L.agency(self.ws)
        self.assertIn("[instruction] Approvers: Alex may approve", agency)
        self.assertIn("names are labels", agency)

    def test_agency_marks_mode_and_rhythm_as_instructions(self):
        agency = L.agency(self.ws)
        self.assertIn("[instruction] Review mode: batch", agency)
        self.assertIn("[instruction] Review rhythm: weekly", agency)


class TestRulesAndDocs(unittest.TestCase):
    def test_workspace_rules_and_skill_carry_the_loop(self):
        agents = (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8")
        for needle in ("## 16. The review loop and who may approve", "living.py nudge .", "living.py reviewed .",
                       "Approvers:", "never review on their behalf"):
            self.assertIn(needle, agents)
        self.assertIn("living.py reviewed .", (REPO / "core/skills/tend/SKILL.md").read_text(encoding="utf-8"))
        self.assertLess(len((REPO / "core/template/AGENTS.md").read_bytes()), 31000)

    def test_agent_rules_stay_under_the_codex_cap_with_every_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            for profile_name in ("student", "professional", "employee", "manager"):
                ws = L.init(Path(tmp) / profile_name, profile_name, "en", True, True, True)
                self.assertLess(len((ws / "AGENTS.md").read_bytes()), 32 * 1024, profile_name)


if __name__ == "__main__":
    unittest.main()

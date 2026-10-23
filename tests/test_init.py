import json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

PROFILES = ("student", "professional", "employee", "manager")
FORBIDDEN = ("Moss", "Riverside", "Maya", "Leo", "Sam Okafor")
TTT_NAME = ("TTT" + "-System", "TTT" + " System")  # split so this file does not contain the banned phrase


def all_text(root):
    return "\n".join(p.read_text() for p in sorted(Path(root).rglob("*")) if p.is_file() and p.suffix != ".pyc")


class InitCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def ws(self, profile="student", **kw):
        kw.setdefault("language", "en")
        return L.init(self.base / profile, profile, **kw)

    def review(self, ws, *args):
        return subprocess.run([sys.executable, "-B", str(ws / "tools/review.py"), "--root", str(ws), *args],
                              capture_output=True, text=True)


class TestInit(InitCase):
    def test_each_profile_inits_and_checks_ok(self):
        for p in PROFILES:
            with self.subTest(profile=p):
                ws = self.ws(p)
                r = self.review(ws, "check")
                self.assertEqual((r.returncode, r.stdout.strip()), (0, "ok"), r.stdout + r.stderr)
                self.assertEqual(self.review(ws, "current").stdout.strip(), "")
                prof = json.loads((ws / ".living/profile.json").read_text())
                self.assertEqual(prof["profile"], p)

    def test_no_demo_names_anywhere(self):
        for p in PROFILES:
            ws = self.ws(p)
            text = all_text(ws) + self.review(ws, "check").stdout + self.review(ws, "current").stdout
            for word in FORBIDDEN + TTT_NAME:
                self.assertNotIn(word, text, f"{word!r} found in {p} workspace")

    def test_starts_as_drafts(self):
        ws = self.ws("manager")
        for f in ("SYSTEM.md", "PRINCIPLES.md"):
            self.assertTrue((ws / f).read_text().startswith("---\nstatus: draft\n---\n"))
        self.assertEqual((ws / "CLAUDE.md").read_text().strip(), "@AGENTS.md")
        principles = (ws / "PRINCIPLES.md").read_text()
        self.assertIn("Third-Run Rule", principles)
        self.assertEqual(len(re.findall(r"^\d\. \*\*", principles, re.M)), 6)

    def test_agents_rules_present(self):
        text = (self.ws() / "AGENTS.md").read_text()
        for s in ("only if it says `status: approved`", "## 8. Language", "## 9. Handover note", "## 10. Calm replies",
                  "kind: new", "target: none", "Task authority is not canonical authority"):
            self.assertIn(s, text)

    def test_refuses_non_empty_dir_and_file(self):
        d = self.base / "full"
        d.mkdir()
        (d / "mine.txt").write_text("keep", encoding="utf-8", newline="\n")
        with self.assertRaises(L.Refusal):
            L.init(d, "student", "en")
        self.assertEqual([p.name for p in d.iterdir()], ["mine.txt"])
        f = self.base / "afile"
        f.write_text("x", encoding="utf-8", newline="\n")
        with self.assertRaises(L.Refusal):
            L.init(f, "student", "en")
        self.assertEqual(f.read_text(), "x")

    def test_accepts_existing_empty_dir(self):
        d = self.base / "empty"
        d.mkdir()
        L.init(d, "student", "en")
        self.assertTrue((d / "AGENTS.md").is_file())

    def test_refuses_inside_the_product_repo(self):
        with self.assertRaises(L.Refusal):
            L.init(REPO / "my-workspace", "student", "en")
        self.assertFalse((REPO / "my-workspace").exists())

    def test_bad_input_creates_nothing(self):
        for kw in ({"profile": "wizard", "language": "en"}, {"profile": "student", "language": "English!"}):
            with self.assertRaises(L.Refusal):
                L.init(self.base / "x", **kw)
        self.assertEqual(list(self.base.iterdir()), [])

    def test_failure_leaves_nothing_behind(self):
        target = self.base / "ws"
        with mock.patch.object(L, "write_manifest", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                L.init(target, "student", "en")
        self.assertEqual(list(self.base.iterdir()), [])
        # an empty folder the user made is left as it was
        target.mkdir()
        with mock.patch.object(L, "write_manifest", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                L.init(target, "student", "en")
        self.assertEqual([p.name for p in self.base.iterdir()], ["ws"])
        self.assertEqual(list(target.iterdir()), [])

    def test_employee_me_is_gitignored_others_not_required(self):
        emp = self.ws("employee")
        self.assertIn("me/", (emp / ".gitignore").read_text().splitlines())
        self.assertTrue((emp / "me/goals.md").is_file())
        self.assertIn("you propose, you do not approve", (emp / "AGENTS.md").read_text().lower())
        mgr = self.ws("manager")
        self.assertFalse((mgr / ".gitignore").exists())
        self.assertTrue((mgr / "me/goals.md").is_file())

    def test_student_has_no_team_files(self):
        ws = self.ws("student")
        names = [p.relative_to(ws).as_posix() for p in ws.rglob("*")]
        self.assertEqual([n for n in names if "team" in n.lower()], [])
        self.assertTrue((ws / "me/goals.md").is_file())
        self.assertTrue((ws / "projects/study-project-template.md").is_file())
        self.assertIn("your own commitments", (ws / "AGENTS.md").read_text())

    def test_professional_and_manager_overlays(self):
        pro = self.ws("professional")
        self.assertTrue((pro / "projects/client-project-template.md").is_file())
        self.assertTrue((pro / "me/goals.md").is_file())
        mgr = self.ws("manager")
        self.assertIn("Roles and approval rules", (mgr / "SYSTEM.md").read_text())
        self.assertTrue((mgr / "SYSTEM.md").read_text().startswith("---\nstatus: draft\n---\n"))
        self.assertTrue((mgr / "knowledge/team-onboarding.md").is_file())

    def test_no_leftover_markers(self):
        for p in PROFILES:
            self.assertNotIn("profile:append", all_text(self.ws(p)))

    def test_language_and_calm_replies_stored(self):
        ws = self.ws("student", language="pl", calm_replies=True)
        self.assertEqual(json.loads((ws / ".living/profile.json").read_text()),
                         {"profile": "student", "language": "pl", "calm_replies": True})
        ws2 = self.ws("professional")
        self.assertFalse(json.loads((ws2 / ".living/profile.json").read_text())["calm_replies"])

    def test_manifest_matches_files(self):
        ws = self.ws("manager")
        m = json.loads((ws / ".living/manifest.json").read_text())
        self.assertEqual(m["kernel_version"], L.KERNEL_VERSION)
        self.assertEqual(m["files"]["tools/review.py"], L.sha256(REPO / "tools/review.py"))
        on_disk = {p.relative_to(ws).as_posix() for p in ws.rglob("*") if p.is_file()} - {".living/manifest.json"}
        self.assertEqual(set(m["files"]), on_disk)
        for rel, h in m["files"].items():
            self.assertEqual(L.sha256(ws / rel), h)

    def test_git_ignores_nothing_under_core(self):
        try:
            r = subprocess.run(["git", "ls-files", "--others", "--ignored", "--exclude-standard", "core/"],
                               cwd=REPO, capture_output=True, text=True)
        except FileNotFoundError:
            self.skipTest("git not available")
        if r.returncode != 0:
            self.skipTest("not a git checkout")
        self.assertEqual(r.stdout.strip(), "")

    def test_template_is_not_modified_by_init(self):
        before = all_text(REPO / "core")
        self.ws("manager")
        self.assertEqual(all_text(REPO / "core"), before)

    def test_cli_init_and_refusal_exit_code(self):
        live = str(REPO / "tools/living.py")
        ok = subprocess.run([sys.executable, "-B", live, "init", str(self.base / "cli"), "--profile", "student",
                             "--language", "en", "--calm-replies"], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("Undo: delete that folder", ok.stdout)
        again = subprocess.run([sys.executable, "-B", live, "init", str(self.base / "cli"), "--profile", "student",
                                "--language", "en"], capture_output=True, text=True)
        self.assertEqual(again.returncode, 2)
        self.assertIn("REFUSED", again.stderr)


class TestValueScore(InitCase):
    SAMPLE = """# Value check questions

| # | Question | Before | After |
| --- | --- | --- | --- |
| 1 | Who approves invoices? | made up | right |
| 2 | Where is the rota? | wrong | right |
| 3 | What is the budget? | made up | don't know |
| 4 | Who is the client? | right | right |
| 5 | When is the deadline? | don't know | |
"""

    def test_prints_table(self):
        ws = self.ws("student")
        (ws / "value-check/questions.md").write_text(self.SAMPLE, encoding="utf-8", newline="\n")
        out = subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "value-score", str(ws)],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        rows = {l.split()[0]: l.split()[1:] for l in out.stdout.splitlines()[1:3]}
        # columns: right, wrong, made up, don't know
        self.assertEqual(rows["before"], ["1", "1", "2", "1"])
        self.assertEqual(rows["after"], ["3", "0", "0", "1"])
        self.assertIn("after: 1 not scored yet", out.stdout)

    def test_fresh_workspace_is_all_unscored(self):
        counts, unscored = L.value_score(self.ws("student"))
        self.assertEqual(sum(sum(c.values()) for c in counts.values()), 0)
        self.assertEqual(unscored, {"before": 5, "after": 5})

    def test_unknown_word_is_refused(self):
        ws = self.ws("student")
        (ws / "value-check/questions.md").write_text(self.SAMPLE.replace("wrong", "meh"), encoding="utf-8", newline="\n")
        with self.assertRaises(L.Refusal):
            L.value_score(ws)

    def test_missing_table_is_refused_not_scored_as_zero(self):
        ws = self.ws("student")
        (ws / "value-check/questions.md").write_text("# Questions\n\nI wrote prose instead of a table.\n", encoding="utf-8", newline="\n")
        with self.assertRaises(L.Refusal):
            L.value_score(ws)

    def test_escaped_pipe_in_question_keeps_columns(self):
        ws = self.ws("student")
        (ws / "value-check/questions.md").write_text(
            "| # | Question | Before | After |\n| --- | --- | --- | --- |\n"
            "| 1 | Do we use A \\| B for invoices? | wrong | right |\n")
        counts, _ = L.value_score(ws)
        self.assertEqual((counts["before"]["wrong"], counts["after"]["right"]), (1, 1))

    def test_existing_empty_folder_is_used_and_restored_on_failure(self):
        target = self.base / "empty"
        target.mkdir()
        with mock.patch.object(L.os, "rename", side_effect=OSError("simulated")):
            with self.assertRaises(OSError):
                L.init(target, "student", "en")
        self.assertTrue(target.is_dir())
        self.assertEqual(list(target.iterdir()), [])
        self.assertEqual(sorted(p.name for p in self.base.iterdir()), ["empty"])
        L.init(target, "student", "en")
        self.assertTrue((target / "AGENTS.md").is_file())


if __name__ == "__main__":
    unittest.main()

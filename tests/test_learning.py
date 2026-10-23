"""Learning mode: coach setting, the practice skill, and the 'working without AI' handbook."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def proposal(title, kind="new", target="none"):
    return (f"---\nstatus: proposed\nkind: {kind}\ntarget: {target}\nevidence: e\nproposed_by: a\ndate: 2026-10-20\n---\n"
            f"\n# Proposal: {title}\n\n## Proposed future state\n\n> {title}.\n\n## Why and open questions\n\nt\n")


class TestCoachSetting(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def profile(self, ws):
        return json.loads((ws / ".living/profile.json").read_text(encoding="utf-8"))

    def test_off_by_default_and_on_when_asked(self):
        self.assertFalse(self.profile(L.init(self.base / "a", "student", "en"))["coach"])
        self.assertTrue(self.profile(L.init(self.base / "b", "student", "en", coach=True))["coach"])

    def test_command_line_flag(self):
        r = subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "init", str(self.base / "c"),
                            "--profile", "employee", "--language", "de", "--coach"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("coach: on", r.stdout)
        self.assertTrue(self.profile(self.base / "c")["coach"])

    def test_upgrade_keeps_the_choice_and_older_workspaces_still_upgrade(self):
        ws = L.init(self.base / "d", "manager", "en", coach=True)
        L.upgrade(ws, apply=True)
        self.assertTrue(self.profile(ws)["coach"])
        old = self.profile(ws)
        del old["coach"]  # a workspace made before coach mode existed
        write(ws / ".living/profile.json", json.dumps(old))
        L.upgrade(ws, apply=True)
        self.assertNotIn("coach", self.profile(ws))

    def test_rules_skill_and_goals_are_in_place(self):
        agents = (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("## 13. Learning: the human keeps their own skills", agents)
        self.assertIn("Never keep scores", agents)
        ws = L.init(self.base / "e", "professional", "en")
        for place in (".claude/skills", ".agents/skills"):
            self.assertTrue((ws / place / "practice/SKILL.md").is_file())
        for goals in REPO.glob("core/**/me/goals.md"):
            with self.subTest(goals=goals.relative_to(REPO).as_posix()):
                text = goals.read_text(encoding="utf-8")
                self.assertTrue("Skills I want to keep" in text or "Fähigkeiten" in text or "Umiejętności" in text)


class TestHandbook(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "manager", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_workspace_says_there_are_no_rules(self):
        text = L.handbook(self.ws)
        self.assertTrue(text.startswith(L.HANDBOOK_MARK))
        self.assertIn("## The rules in force (0)", text)
        self.assertIn("nothing here is a rule", text)
        self.assertIn("`SYSTEM.md`: a draft, not a rule yet.", text)
        self.assertIn("## Doing it by hand", text)

    def test_lists_current_rules_only_and_what_waits(self):
        write(self.ws / "proposals/2026-10-20-fridays.md", proposal("Reports go out on Fridays"))
        R.review(self.ws, "proposals/2026-10-20-fridays.md", "approve", "Ann", date="2026-10-20")
        old = R.current_decisions(self.ws)[0]
        write(self.ws / "proposals/2026-10-21-mondays.md",
              proposal("Reports go out on Mondays", "replace", old).replace(
                  "evidence:", f"target_sha256: {L.sha256(self.ws / old)}\nevidence:"))
        R.review(self.ws, "proposals/2026-10-21-mondays.md", "approve", "Ben", date="2026-10-21")
        write(self.ws / "proposals/2026-10-22-calls.md", proposal("Calls are recorded"))
        L.add_module(self.ws, "weekly-update", apply=True)
        L.runs(self.ws, add="weekly-update")
        write(self.ws / "handover/LATEST.md", "# Handover\n\n**Next step:** call the printer\n")
        before = snapshot(self.ws)
        text = L.handbook(self.ws)
        self.assertEqual(snapshot(self.ws), before)
        self.assertIn("## The rules in force (1)", text)
        self.assertIn("Reports go out on Mondays.", text)
        self.assertNotIn("Reports go out on Fridays.", text)  # replaced: history, not a rule
        self.assertIn("Calls are recorded (`proposals/2026-10-22-calls.md`): not a rule", text)
        self.assertIn("01-gather → 02-draft", text)
        self.assertIn("'weekly-update' (counted 1 times", text)
        self.assertIn("call the printer", text)

    def test_saved_only_outside_the_workspace_and_never_over_other_files(self):
        with self.assertRaises(L.Refusal):
            L.write_handbook(self.ws, self.ws / "handbook.md", L.handbook(self.ws))
        other = self.base / "notes.md"
        write(other, "my notes\n")
        with self.assertRaises(L.Refusal):
            L.write_handbook(self.ws, other, L.handbook(self.ws))
        self.assertEqual(other.read_text(encoding="utf-8"), "my notes\n")
        with self.assertRaises(L.Refusal):
            L.write_handbook(self.ws, self.base / "handbook.zip", "x")
        target = self.base / "handbook.md"
        L.write_handbook(self.ws, target, L.handbook(self.ws))
        L.write_handbook(self.ws, target, L.handbook(self.ws) + "\nagain")  # a previous handbook may be replaced
        self.assertTrue(target.read_text(encoding="utf-8").endswith("again\n"))

    def test_command_line(self):
        run = lambda *a: subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "handbook", str(self.ws), *a],
                                        capture_output=True, text=True, encoding="utf-8")
        self.assertIn("# Working without AI", run().stdout)
        saved = run("--out", str(self.base / "h.md"))
        self.assertEqual(saved.returncode, 0, saved.stderr)
        self.assertIn("It is a copy, not the rules.", saved.stdout)
        self.assertEqual(run("--out", str(self.ws / "h.md")).returncode, 2)


if __name__ == "__main__":
    unittest.main()

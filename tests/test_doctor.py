"""The read-only workspace health check."""
import shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


class TestDoctor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "student", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def levels(self):
        return {(lvl, msg.split(":")[0].split(" ")[0]) for lvl, msg in L.doctor(self.ws)}

    def test_fresh_workspace_only_warns_about_drafts(self):
        before = snapshot(self.ws)
        res = L.doctor(self.ws)
        self.assertEqual(sorted(lvl for lvl, _ in res), ["WARN", "WARN"])
        self.assertTrue(all("not approved yet" in m for _, m in res))
        self.assertEqual(snapshot(self.ws), before, "doctor must not write")

    def test_approved_drafts_and_modules_are_clean(self):
        for f in ("SYSTEM.md", "PRINCIPLES.md"):
            p = self.ws / f
            p.write_text(p.read_text(encoding="utf-8").replace("status: draft", "status: approved", 1), encoding="utf-8", newline="\n")
        for mid in ("weekly-update", "meeting-notes", "staged-learning"):
            L.add_module(self.ws, mid, apply=True)
        self.assertEqual(L.doctor(self.ws), [])
        self.assertEqual(L.format_doctor([]), "All good: no problems found.")

    def test_finds_real_problems(self):
        L.add_module(self.ws, "staged-learning", apply=True)
        (self.ws / "workflows/x").mkdir()
        (self.ws / "workflows/x/AGENTS.md").write_text("rules\n", encoding="utf-8", newline="\n")
        (self.ws / "knowledge/copied.md").write_text("> **DEMO — fictional sandbox, not your workspace.**\n", encoding="utf-8", newline="\n")
        (self.ws / "lessons/active.md").write_text("## Active lessons\n\n" + "".join(f"- lesson {i}\n" for i in range(21)), encoding="utf-8", newline="\n")
        with open(self.ws / "tools/review.py", "a") as f:
            f.write("\n# edited\n")
        L.new_workflow(self.ws, "plan", ["a", "b"], apply=True)
        (self.ws / "workflows/plan/01-a/CONTEXT.md").write_text("line\n" * 85, encoding="utf-8", newline="\n")
        (self.ws / "proposals/2026-10-23-new-rule.md").write_text(
            "---\nstatus: proposed\nkind: new\ntarget: none\nevidence: x\nproposed_by: agent\ndate: 2026-10-23\n---\n"
            "\n# Proposal: X\n\n## Proposed future state\n\n> Rule.\n\n## Why and open questions\n\nx\n")
        text = L.format_doctor(L.doctor(self.ws))
        for expected in ("ERROR: workflows/x/AGENTS.md", "ERROR: knowledge/copied.md",
                         "WARN: lessons/active.md has 21 lessons", "WARN: tools/review.py differs",
                         "WARN: workflows/plan/01-a/CONTEXT.md has 85 lines", "still has",
                         "INFO: proposals/2026-10-23-new-rule.md is proposed"):
            self.assertIn(expected, text)

    def test_routing_and_manifest_out_of_sync(self):
        L.add_module(self.ws, "weekly-update", apply=True)
        r = self.ws / "CONTEXT-ROUTING.md"
        r.write_text(L.routing_without(r.read_text(encoding="utf-8"), "weekly-update"), encoding="utf-8", newline="\n")
        shutil.rmtree(self.ws / "workflows/weekly-update/01-gather")
        text = L.format_doctor(L.doctor(self.ws))
        self.assertIn("ERROR: module weekly-update is installed but has no row", text)
        self.assertIn("WARN: module weekly-update: 2 file(s) missing", text)

    def test_cli_exit_codes(self):
        run = lambda: subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "doctor", str(self.ws)],
                                     capture_output=True, text=True)
        self.assertEqual(run().returncode, 0)
        (self.ws / "workflows/CLAUDE.md").write_text("x\n", encoding="utf-8", newline="\n")
        r = run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("1 error(s)", r.stdout)


if __name__ == "__main__":
    unittest.main()

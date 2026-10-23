"""The write guard that Claude Code and Codex hooks run before an agent changes a file."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class GuardCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "student", "en")
        write(self.ws / "decisions/2026-10-01-x.md", "---\nstatus: approved\n---\n\n# X\n\n## Rule\n\nR.\n")
        write(self.ws / "proposals/2026-10-02-p.md", "---\nstatus: proposed\nkind: new\ntarget: none\n---\n\n# Proposal: P\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_guard(self, event):
        r = subprocess.run([sys.executable, "-B", str(self.ws / "tools/guard.py")], input=json.dumps(event),
                           capture_output=True, text=True, cwd=self.ws)
        return r.returncode, r.stderr

    def blocked(self, event):
        code, err = self.run_guard(event)
        self.assertEqual(code, 2, f"expected a block for {event}")
        self.assertIn("Living System guard: blocked.", err)
        return err

    def allowed(self, event):
        code, err = self.run_guard(event)
        self.assertEqual((code, err), (0, ""), f"expected no block for {event}")


class TestClaudeEdits(GuardCase):
    def test_decisions_are_never_written_by_an_agent(self):
        for path in ("decisions/2026-10-01-x.md", "decisions/new.md", str(self.ws / "decisions/x.md"),
                     "projects/../decisions/x.md", "decisions\\x.md"):
            with self.subTest(path=path):
                err = self.blocked({"tool_name": "Write", "tool_input": {"file_path": path, "content": "x"}})
                self.assertIn("Write a proposal instead", err)
        self.blocked({"tool_name": "Edit", "tool_input": {"file_path": "decisions/2026-10-01-x.md",
                                                          "old_string": "R.", "new_string": "S."}})

    def test_only_the_human_approves_system_and_principles(self):
        for f in ("SYSTEM.md", "PRINCIPLES.md"):
            with self.subTest(file=f):
                self.blocked({"tool_name": "Edit", "tool_input": {"file_path": f, "old_string": "status: draft",
                                                                  "new_string": "status: approved"}})
                self.allowed({"tool_name": "Edit", "tool_input": {"file_path": f, "old_string": "# ",
                                                                  "new_string": "# "}})
        self.blocked({"tool_name": "MultiEdit", "tool_input": {"file_path": "SYSTEM.md", "edits": [
            {"old_string": "status: draft", "new_string": "status: approved"}]}})

    def test_proposal_outcomes_come_only_from_review(self):
        self.allowed({"tool_name": "Write", "tool_input": {"file_path": "proposals/2026-10-03-new.md",
                                                           "content": "---\nstatus: proposed\n---\n"}})
        self.blocked({"tool_name": "Edit", "tool_input": {"file_path": "proposals/2026-10-02-p.md",
                                                          "old_string": "status: proposed", "new_string": "status: promoted"}})

    def test_the_guard_and_review_tool_are_protected(self):
        for f in ("tools/guard.py", "tools/review.py", ".claude/settings.json", ".codex/hooks.json"):
            with self.subTest(file=f):
                self.blocked({"tool_name": "Write", "tool_input": {"file_path": f, "content": ""}})

    def test_ordinary_work_is_allowed(self):
        for f in ("knowledge/a.md", "projects/p.md", "handover/LATEST.md", "workflows/w/CONTEXT.md",
                  str(Path(self.tmp.name) / "outside.md")):
            with self.subTest(file=f):
                self.allowed({"tool_name": "Write", "tool_input": {"file_path": f, "content": "x"}})
        self.allowed({"tool_name": "Read", "tool_input": {"file_path": "decisions/2026-10-01-x.md"}})


class TestCodexPatches(GuardCase):
    def patch(self, body):
        return {"tool_name": "apply_patch", "tool_input": {"command": f"*** Begin Patch\n{body}\n*** End Patch\n"}}

    def test_patches_into_decisions_are_blocked(self):
        self.blocked(self.patch("*** Add File: decisions/new.md\n+---\n+status: approved\n+---"))
        self.blocked(self.patch("*** Delete File: decisions/2026-10-01-x.md"))
        self.blocked(self.patch("*** Update File: proposals/2026-10-02-p.md\n*** Move to: decisions/p.md\n@@\n-a\n+b"))

    def test_patches_that_approve_are_blocked_and_others_pass(self):
        self.blocked(self.patch("*** Update File: SYSTEM.md\n@@\n-status: draft\n+status: approved"))
        self.blocked(self.patch("*** Update File: proposals/2026-10-02-p.md\n@@\n-status: proposed\n+status: rejected"))
        self.allowed(self.patch("*** Update File: SYSTEM.md\n@@\n-(name)\n+Alex"))
        self.allowed(self.patch("*** Add File: knowledge/vat.md\n+# VAT"))

    def test_patch_sent_through_the_shell_tool(self):
        self.blocked({"tool_name": "Bash", "tool_input": {
            "command": "apply_patch <<'EOF'\n*** Begin Patch\n*** Add File: decisions/x.md\n+x\n*** End Patch\nEOF"}})


class TestShell(GuardCase):
    def cmd(self, c):
        return {"tool_name": "Bash", "tool_input": {"command": c}}

    def test_reading_and_the_review_tool_are_fine(self):
        for c in ("cat decisions/2026-10-01-x.md 2>&1", "ls decisions/ >/dev/null", "grep -r Rule decisions/",
                  "python3 tools/review.py review proposals/2026-10-02-p.md --outcome approve --by Me",
                  "python3 tools/review.py current 2>&1 | head", "cp decisions/2026-10-01-x.md /tmp/copy.md",
                  "python3 tools/guard.py < event.json"):
            with self.subTest(cmd=c):
                self.allowed(self.cmd(c))

    def test_changing_decisions_or_the_guard_is_blocked(self):
        for c in ("rm decisions/2026-10-01-x.md", "echo x > decisions/new.md", "echo x >> ./decisions/x.md",
                  "sed -i 's/R/S/' decisions/2026-10-01-x.md", "cp proposals/2026-10-02-p.md decisions/p.md",
                  "mv decisions/2026-10-01-x.md /tmp/", "python3 -c \"open('decisions/x.md','w').write('x')\"",
                  "rm tools/guard.py", "echo {} > .claude/settings.json", "Remove-Item decisions\\x.md",
                  "cd projects && rm ../decisions/2026-10-01-x.md"):
            with self.subTest(cmd=c):
                self.blocked(self.cmd(c))

    def test_unreadable_input_is_left_to_the_normal_prompts(self):
        r = subprocess.run([sys.executable, "-B", str(self.ws / "tools/guard.py")], input="not json",
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)


class TestWorkspaceWiring(GuardCase):
    def test_both_agents_are_wired_to_the_guard(self):
        claude = json.loads((self.ws / ".claude/settings.json").read_text(encoding="utf-8"))
        codex = json.loads((self.ws / ".codex/hooks.json").read_text(encoding="utf-8"))
        for cfg, words in ((claude, ("Edit", "Write", "Bash")), (codex, ("apply_patch", "Bash"))):
            group = cfg["hooks"]["PreToolUse"][0]
            for w in words:
                self.assertIn(w, group["matcher"])
            self.assertIn("tools/guard.py", group["hooks"][0]["command"])
        self.assertFalse([m for lvl, m in L.doctor(self.ws) if "guard" in m])

    @unittest.skipIf(os.name == "nt", "the hook command is a POSIX shell command")
    def test_the_real_hook_command_blocks(self):
        cmd = json.loads((self.ws / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        r = subprocess.run(["sh", "-c", cmd], input=json.dumps({"tool_name": "Write", "tool_input": {
            "file_path": "decisions/x.md", "content": "x"}}), capture_output=True, text=True, cwd=self.ws,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(self.ws)})
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_doctor_reports_a_missing_guard(self):
        (self.ws / "tools/guard.py").unlink()
        self.assertIn("tools/guard.py, which is missing", L.format_doctor(L.doctor(self.ws)))

    def test_review_still_works_with_the_guard_installed(self):
        rel, _ = L.propose(self.ws, "new", "First", "A rule.", "test", date="2026-10-24", apply=True)
        R = L.review_tool()
        self.assertEqual(R.review(self.ws, rel, "approve", "Owner", date="2026-10-24")[0], "promoted")


if __name__ == "__main__":
    unittest.main()

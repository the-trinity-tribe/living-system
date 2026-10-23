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
        self.assertIn("tools/guard.py is missing", L.format_doctor(L.doctor(self.ws)))

    def test_review_still_works_with_the_guard_installed(self):
        rel, _ = L.propose(self.ws, "new", "First", "A rule.", "test", date="2026-10-24", apply=True)
        R = L.review_tool()
        self.assertEqual(R.review(self.ws, rel, "approve", "Owner", date="2026-10-24")[0], "promoted")



class TestFourthReview(GuardCase):
    """Bypasses and false blocks found in the fourth review."""

    def cmd(self, c, cwd=None):
        event = {"tool_name": "Bash", "tool_input": {"command": c}}
        if cwd:
            event["cwd"] = str(cwd)
        return event

    def test_shell_cannot_approve_drafts_or_set_outcomes(self):
        for c in ("sed -i 's/status: draft/status: approved/' SYSTEM.md",
                  "sed -i 's/status: proposed/status: promoted/' proposals/2026-10-02-p.md",
                  "printf '---\nstatus: approved\n---\n' > PRINCIPLES.md",
                  "python3 -c \"import pathlib; p=pathlib.Path('SYSTEM.md'); p.write_text(p.read_text().replace('draft','approved'))\""):
            with self.subTest(cmd=c):
                self.blocked(self.cmd(c))
        self.allowed(self.cmd("sed -i 's/(name)/Alex/' SYSTEM.md"))

    def test_patch_text_does_not_hide_other_commands(self):
        self.blocked(self.cmd("printf '%s\\n' '*** Begin Patch'; rm decisions/2026-10-01-x.md"))

    def test_removing_folders_that_hold_protected_files(self):
        for c in ("rm -rf .claude", "rm -rf tools", "rm -rf .codex", "rm -rf decisions", "rm -rf .", "mv tools /tmp/t"):
            with self.subTest(cmd=c):
                self.blocked(self.cmd(c))
        self.allowed(self.cmd("rm -rf workflows/old"))

    def test_patch_result_is_checked_not_only_added_lines(self):
        write(self.ws / "knowledge/approved.md", "---\nstatus: approved\n---\n\n# Old title\n")
        move = {"tool_name": "apply_patch", "tool_input": {"command":
                "*** Begin Patch\n*** Update File: knowledge/approved.md\n*** Move to: PRINCIPLES.md\n@@\n-# Old title\n+# New title\n*** End Patch\n"}}
        self.blocked(move)
        example = {"tool_name": "apply_patch", "tool_input": {"command":
                   "*** Begin Patch\n*** Update File: proposals/2026-10-02-p.md\n@@\n # Proposal: P\n+\n+Example: `status: rejected` means closed.\n*** End Patch\n"}}
        self.allowed(example)

    def test_quotes_line_breaks_cd_and_copy_options(self):
        spaced = Path(self.tmp.name) / "with space"
        spaced.mkdir()
        ws2 = L.init(spaced / "ws", "student", "en")
        r = subprocess.run([sys.executable, "-B", str(ws2 / "tools/guard.py")], input=json.dumps(self.cmd(
            f'echo changed > "{ws2}/decisions/new.md"')), capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.blocked(self.cmd("cd decisions\nrm 2026-10-01-x.md"))
        self.blocked(self.cmd("cp projects/p.md decisions/x.md --verbose"))
        self.blocked(self.cmd("cp --target-directory=decisions projects/p.md"))
        self.blocked(self.cmd("cp -t decisions projects/p.md"))

    @unittest.skipUnless(os.name != "nt", "creating links needs extra rights on Windows")
    def test_writing_through_a_link_inside_decisions(self):
        outside = Path(self.tmp.name) / "outside.md"
        outside.write_text("x", encoding="utf-8")
        (self.ws / "decisions/linked.md").symlink_to(outside)
        self.blocked({"tool_name": "Write", "tool_input": {"file_path": "decisions/linked.md", "content": "y"}})

    def test_windows_drive_paths_are_read_as_paths(self):
        sys.path.insert(0, str(self.ws / "tools"))
        import guard as G
        self.assertEqual(G.split_commands(r"copy x C:\Users\RUNNER~1\org\decisions\y.md"),
                         [["copy", "x", "C:/Users/RUNNER~1/org/decisions/y.md"]])

    def test_odd_encoding_does_not_crash_the_guard(self):
        (self.ws / "SYSTEM.md").write_bytes(b"---\nstatus: draft\n---\n\n\x96 dash\n")
        self.blocked({"tool_name": "Write", "tool_input": {"file_path": "SYSTEM.md",
                                                           "content": "---\nstatus: approved\n---\n"}})

    def test_reading_and_text_that_mentions_commands_are_not_blocked(self):
        for c in ("python3 -c \"print(open('decisions/2026-10-01-x.md').read())\"",
                  "grep 'rm' decisions/2026-10-01-x.md",
                  "python3 tools/review.py review proposals/2026-10-02-p.md --outcome approve --by Me --note 'rm old wording'",
                  "cat decisions/2026-10-01-x.md | wc -l", "echo 'the decisions/ folder is protected'"):
            with self.subTest(cmd=c):
                self.allowed(self.cmd(c))

    @unittest.skipIf(os.name == "nt", "the hook command is a POSIX shell command")
    def test_codex_hook_works_from_a_subfolder_and_without_a_guard(self):
        cmd = json.loads((self.ws / ".codex/hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        sub = self.ws / "projects"
        block = json.dumps({"tool_name": "Bash", "cwd": str(sub), "tool_input": {"command": "rm ../decisions/2026-10-01-x.md"}})
        read = json.dumps({"tool_name": "Bash", "cwd": str(sub), "tool_input": {"command": "ls"}})
        run = lambda payload: subprocess.run(["sh", "-c", cmd], input=payload, capture_output=True, text=True, cwd=sub)
        self.assertEqual(run(block).returncode, 2)
        self.assertEqual(run(read).returncode, 0)
        (self.ws / "tools/guard.py").unlink()
        self.assertEqual(run(read).returncode, 0, "a missing guard must not block all work")

    def test_doctor_checks_the_hooks_really_run_the_guard_and_protect_restores(self):
        (self.ws / ".codex/hooks.json").write_text('{"hooks": {}}', encoding="utf-8")
        self.assertIn(".codex/hooks.json does not run tools/guard.py", L.format_doctor(L.doctor(self.ws)))
        (self.ws / ".claude/settings.json").unlink()
        (self.ws / "tools/guard.py").unlink()
        self.assertEqual(sorted(L.protect(self.ws)), [".claude/settings.json", "tools/guard.py"])
        self.assertFalse((self.ws / "tools/guard.py").exists(), "plan only without --apply")
        L.protect(self.ws, apply=True)
        self.assertTrue((self.ws / "tools/guard.py").is_file())
        self.assertFalse([m for _, m in L.doctor(self.ws) if "guard.py is missing" in m or "settings.json is missing" in m])
        self.assertIn('{"hooks": {}}', (self.ws / ".codex/hooks.json").read_text(encoding="utf-8"), "never overwrites")

if __name__ == "__main__":
    unittest.main()

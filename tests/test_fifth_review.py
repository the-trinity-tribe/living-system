"""Regression tests for the fifth code review (catch-up, learning, scan, record, connected workspaces)."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def proposal(title, by="a", kind="new", target="none", sha=None):
    extra = f"target_sha256: {sha}\n" if sha else ""
    return (f"---\nstatus: proposed\nkind: {kind}\ntarget: {target}\n{extra}evidence: e\nproposed_by: {by}\ndate: 2026-10-20\n"
            f"---\n\n# Proposal: {title}\n\n## Proposed future state\n\n> {title}.\n\n## Why and open questions\n\nt\n")


class Pair(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.base = base
        self.org = L.init(base / "org", "manager", "en", team=True)
        self.me = L.init(base / "me", "employee", "en")
        L.link(self.me, self.org, "sales")

    def tearDown(self):
        self.tmp.cleanup()

    def guard(self, ws, event):
        return subprocess.run([sys.executable, "-B", str(ws / "tools/guard.py")], input=json.dumps(event),
                              capture_output=True, text=True, cwd=ws).returncode

    def bash(self, ws, command):
        return self.guard(ws, {"tool_name": "Bash", "tool_input": {"command": command}})


class TestGuard(Pair):
    def test_secrets_in_shell_writes_are_blocked(self):  # finding 3
        self.assertEqual(self.bash(self.me, "printf '%s\\n' 'password: Winter2026x' > knowledge/key.md"), 2)
        self.assertEqual(self.bash(self.me, "echo 'password: Winter2026x' | tee projects/x.md"), 2)
        self.assertEqual(self.bash(self.me, "echo 'meeting moved' > projects/x.md"), 0)
        self.assertEqual(self.bash(self.me, "echo 'password: Winter2026x'"), 0)  # writes nothing

    def test_inline_code_cannot_reach_the_company_or_role_knowledge(self):  # finding 4
        code = f"from pathlib import Path; Path('{self.org.as_posix()}/projects/x.md').write_text('changed')"
        self.assertEqual(self.bash(self.me, f'python3 -c "{code}"'), 2)
        code = "from pathlib import Path; Path('roles/sales/knowledge/x.md').write_text('changed')"
        self.assertEqual(self.bash(self.org, f'python3 -c "{code}"'), 2)

    def test_team_and_link_settings_are_the_humans(self):  # findings 5 and 6
        prof = (self.org / ".living/profile.json").read_text(encoding="utf-8")
        off = prof.replace('"team": true', '"team": false')
        self.assertEqual(self.guard(self.org, {"tool_name": "Write", "tool_input": {
            "file_path": ".living/profile.json", "content": off}}), 2)
        coach = prof.replace('"coach": false', '"coach": true')
        self.assertEqual(self.guard(self.org, {"tool_name": "Write", "tool_input": {
            "file_path": ".living/profile.json", "content": coach}}), 0)
        self.assertEqual(self.guard(self.me, {"tool_name": "Write", "tool_input": {
            "file_path": ".living/local.json", "content": json.dumps({"product_folder": str(REPO)})}}), 2)
        self.assertEqual(self.bash(self.me, "rm .living/local.json"), 2)
        self.assertEqual(self.bash(self.org, "echo '{}' > .living/profile.json"), 2)

    def test_unreconstructable_patch_is_still_scanned_for_secrets(self):  # finding 7
        write(self.me / "projects/x.md", "ordinary line\n")
        patch = ("*** Begin Patch\n*** Update File: projects/x.md\n@@\n-ordinary line \n+password: Winter2026x\n"
                 "*** End Patch\n")
        self.assertEqual(self.guard(self.me, {"tool_name": "apply_patch", "tool_input": {"command": patch}}), 2)

    def test_recursive_copy_into_a_folder_is_checked_inside(self):  # finding 8
        write(self.org / "staged/roles/sales/knowledge/x.md", "x\n")
        self.assertEqual(self.bash(self.org, "cp -r staged/roles ."), 2)
        self.assertEqual(self.bash(self.org, "cp -r staged/decisions ."), 2)
        self.assertEqual(self.bash(self.org, "cp staged/notes.md projects/"), 0)

    def test_password_manager_references_are_fine(self):  # finding 19
        for text in ("password: 1Password", "token: Bitwarden", "Passwort: KeePassXC"):
            with self.subTest(text=text):
                self.assertEqual(self.guard(self.me, {"tool_name": "Write", "tool_input": {
                    "file_path": "knowledge/where.md", "content": text + "\n"}}), 0)


class TestRecord(Pair):
    def approve(self, ws, name, title, by="Ali"):
        write(ws / f"proposals/2026-10-20-{name}.md", proposal(title))
        return R.review(ws, f"proposals/2026-10-20-{name}.md", "approve", by, date="2026-10-21")

    @unittest.skipIf(os.name == "nt", "links need extra rights on Windows")
    def test_a_linked_decisions_folder_is_refused_for_every_outcome(self):  # finding 2
        target = self.base / "elsewhere"
        target.mkdir()
        for f in (self.me / "decisions").glob("*"):
            f.unlink()
        (self.me / "decisions").rmdir()
        (self.me / "decisions").symlink_to(target)
        write(self.me / "proposals/2026-10-20-x.md", proposal("X"))
        with self.assertRaises(R.Refusal):
            R.review(self.me, "proposals/2026-10-20-x.md", "reject", "Sam")
        self.assertEqual(list(target.iterdir()), [])

    def test_editing_the_last_line_shows_up(self):  # finding 9
        self.approve(self.org, "a", "A")
        self.approve(self.org, "b", "B")
        path = self.org / R.RECORD
        lines = path.read_text(encoding="utf-8").splitlines()
        write(path, lines[0] + "\n" + lines[1].replace('"Ali"', '"Bob"') + "\n")
        self.assertEqual(R.verify(self.org)[0][0], "ERROR")

    def test_damaged_or_bom_team_settings_never_switch_the_rule_off(self):  # finding 10
        write(self.org / "proposals/2026-10-20-a.md", proposal("A", by="Kim"))
        prof = self.org / ".living/profile.json"
        prof.write_bytes(b"\xef\xbb\xbf" + prof.read_bytes())
        with self.assertRaises(R.Refusal):
            R.review(self.org, "proposals/2026-10-20-a.md", "approve", "Kim")
        write(prof, "{damaged")
        with self.assertRaises(R.Refusal):
            R.review(self.org, "proposals/2026-10-20-a.md", "approve", "Ali")

    def test_a_reviewed_proposal_missing_from_the_record_is_reported(self):  # finding 12
        self.approve(self.org, "a", "A")
        write(self.org / "proposals/2026-10-20-b.md", proposal("B").replace("status: proposed", "status: rejected"))
        self.assertTrue(any("proposals/2026-10-20-b.md" in m for _, m in R.verify(self.org)))

    def test_verify_waits_for_a_running_review(self):  # finding 18
        self.approve(self.org, "a", "A")
        (self.org / ".review.lock").touch()
        self.assertEqual([lvl for lvl, _ in R.verify(self.org)], ["INFO"])


class TestShare(Pair):
    def test_front_matter_and_label_are_checked_too(self):  # finding 1
        write(self.me / "knowledge/a.md", "---\nlast_verified: alice@client.test password: Winter2026x\n---\n\n# A\n\nok\n")
        rel, text = L.share(self.me, "knowledge/a.md")
        self.assertNotIn("alice", text)
        self.assertNotIn("Winter", text)
        with self.assertRaises(L.Refusal):
            L.share(self.me, "knowledge/a.md", shared_as="+49 170 1234567")

    def test_more_phone_formats(self):  # finding 13
        for number in ("212-555-0123", "020 7946 0958", "(212) 555-0123"):
            with self.subTest(number=number):
                self.assertTrue(L.personal_data(f"Call {number} today."))
        for fine in ("On 2026-10-24 at 10:30", "ISBN 978-3-16-148410-0", "Q4 2026, 15 percent"):
            with self.subTest(fine=fine):
                self.assertEqual(L.personal_data(fine), [])

    def test_accept_is_all_or_nothing(self):  # finding 15
        write(self.me / "knowledge/a.md", "# A\n\nok\n")
        rel, _ = L.share(self.me, "knowledge/a.md", apply=True)
        real = Path.unlink

        def failing(path, *a, **kw):
            if path.name.endswith("-a.md") and "inbox" in path.parts:
                raise PermissionError("read-only")
            return real(path, *a, **kw)
        from unittest import mock
        with mock.patch.object(Path, "unlink", failing), self.assertRaises(PermissionError):
            L.role_review(self.org, rel, "accept", "Kim")
        self.assertFalse((self.org / "roles/sales/knowledge/a.md").exists())
        self.assertTrue((self.org / rel).is_file())

    def test_a_refused_link_changes_nothing(self):  # finding 16
        bad = L.init(self.base / "bad", "manager", "en")
        (bad / ".living/profile.json").unlink()
        before = (self.me / ".living/local.json").read_bytes()
        with self.assertRaises(L.Refusal):
            L.link(self.me, bad, "other")
        self.assertEqual((self.me / ".living/local.json").read_bytes(), before)

    def test_only_the_lessons_file_itself(self):  # finding 24
        write(self.me / "lessons/active.md.backup.md", "# B\n")
        with self.assertRaises(L.Refusal):
            L.share(self.me, "lessons/active.md.backup.md")

    def test_ordinary_role_text_is_not_steering(self):  # finding 20
        write(self.me / "knowledge/intro.md", "# Welcome\n\nYou are now an account manager. Start with the client list.\n")
        L.share(self.me, "knowledge/intro.md")

    def test_bom_local_settings_keep_the_link_through_upgrade(self):  # finding 11
        path = self.me / ".living/local.json"
        path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
        L.upgrade(self.me, apply=True)
        self.assertEqual(L.org_folder(self.me), self.org.resolve())


class TestReading(Pair):
    def test_utf16_files_are_scanned(self):  # finding 17
        (self.me / "knowledge/w.md").write_bytes("password: Winter2026x\n".encode("utf-16"))
        self.assertEqual([lvl for lvl, *_ in L.scan(self.me, ["knowledge/w.md"])], ["ERROR"])

    def test_evidence_shows_only_real_dates(self):  # finding 14
        write(self.me / "proposals/2026-10-20-x.md",
              proposal("X").replace("date: 2026-10-20", "date: 2026-01-01 (Client Acme /home/someone/private)"))
        text = L.evidence(self.me)
        self.assertNotIn("Acme", text)
        self.assertNotIn("/home/", text)

    def test_changed_material_comes_back_on_the_onboarding_path(self):  # finding 21
        system = self.org / "SYSTEM.md"
        write(system, system.read_text(encoding="utf-8").replace("status: draft", "status: approved", 1))
        L.onboard(self.me, done="company:SYSTEM.md")
        self.assertEqual(L.onboard(self.me)[1], 1)
        write(system, system.read_text(encoding="utf-8") + "\nA new line about who approves.\n")
        nxt, done, total, _ = L.onboard(self.me)
        self.assertEqual(done, 0)
        self.assertEqual(nxt[0][1], "company:SYSTEM.md")

    def test_handbook_has_company_rules_and_approved_principles(self):  # finding 22
        write(self.org / "proposals/2026-10-20-export.md", proposal("Nothing leaves the company drive"))
        R.review(self.org, "proposals/2026-10-20-export.md", "approve", "Ali")
        principles = self.me / "PRINCIPLES.md"
        write(principles, principles.read_text(encoding="utf-8").replace("status: draft", "status: approved", 1))
        text = L.handbook(self.me)
        self.assertIn("Nothing leaves the company drive.", text)
        self.assertIn("`PRINCIPLES.md` (approved)", text)
        self.assertNotIn("No approved rules yet", text)

    @unittest.skipIf(os.name == "nt", "links need extra rights on Windows")
    def test_a_dangling_link_is_not_followed(self):  # finding 23
        link = self.base / "handbook.md"
        link.symlink_to(self.base / "outside.md")
        with self.assertRaises(L.Refusal):
            L.write_handbook(self.me, link, L.handbook(self.me))
        self.assertFalse((self.base / "outside.md").exists())


if __name__ == "__main__":
    unittest.main()

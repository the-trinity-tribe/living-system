"""Bringing an existing workspace up to date without touching the human's work.

An older install is simulated by giving a file older content and recording that content's
hash in the manifest, exactly as an older `init` or `add` would have left it.
"""
import json, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


def snapshot(root):
    out = {}
    for p in sorted(Path(root).rglob("*")):
        out[str(p.relative_to(root)) + ("/" if p.is_dir() else "")] = p.read_bytes() if p.is_file() else b""
    return out


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "employee", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self):
        return json.loads((self.ws / ".living/manifest.json").read_text())

    def save(self, m):
        (self.ws / ".living/manifest.json").write_text(json.dumps(m, indent=2) + "\n")

    def make_old(self, rel, old_text, module=None):
        """Pretend an older version installed `rel` with `old_text` and the human never touched it."""
        (self.ws / rel).write_text(old_text)
        m = self.manifest()
        files = m["files"] if module is None else m["modules"][module]["files"]
        files[rel] = L.sha256_bytes(old_text.encode())
        self.save(m)

    def actions(self, plan):
        return {(a, rel) for a, rel, _, _ in plan if a != "same"}


class TestUpgrade(Case):
    def test_fresh_workspace_is_up_to_date_and_untouched(self):
        before = snapshot(self.ws)
        plan = L.upgrade(self.ws, apply=True)
        self.assertEqual(self.actions(plan), set())
        self.assertEqual(L.format_upgrade_plan(plan), "Already up to date.")
        self.assertEqual(snapshot(self.ws), before)

    def test_unchanged_old_file_is_updated_after_apply_only(self):
        new = (self.ws / "AGENTS.md").read_text()
        self.make_old("AGENTS.md", "# AGENTS.md\n\nold rules\n")
        before = snapshot(self.ws)
        plan = L.upgrade(self.ws)
        self.assertEqual(self.actions(plan), {("update", "AGENTS.md")})
        self.assertEqual(snapshot(self.ws), before, "the plan writes nothing")
        L.upgrade(self.ws, apply=True)
        self.assertEqual((self.ws / "AGENTS.md").read_text(), new)
        self.assertEqual(self.actions(L.upgrade(self.ws)), set(), "a second upgrade has nothing to do")

    def test_edited_file_is_kept_and_new_version_saved_beside(self):
        new = (self.ws / "AGENTS.md").read_text()
        (self.ws / "AGENTS.md").write_text(new + "\nMy own extra rule.\n")
        self.make_old_hash_only("AGENTS.md", "older text\n")
        L.upgrade(self.ws, apply=True)
        self.assertIn("My own extra rule.", (self.ws / "AGENTS.md").read_text())
        self.assertEqual((self.ws / ".living/upgrade/AGENTS.md").read_text(), new)
        self.assertIn(("keep", "AGENTS.md"), self.actions(L.upgrade(self.ws)))

    def make_old_hash_only(self, rel, old_text):
        m = self.manifest()
        m["files"][rel] = L.sha256_bytes(old_text.encode())
        self.save(m)

    def test_deleted_file_stays_deleted_and_new_file_is_added(self):
        (self.ws / "value-check/log.md").unlink()
        self.make_old_hash_only("value-check/log.md", "older\n")
        (self.ws / ".living/catalog.md").unlink()
        m = self.manifest()
        del m["files"][".living/catalog.md"]
        self.save(m)
        plan = L.upgrade(self.ws, apply=True)
        self.assertIn(("gone", "value-check/log.md"), self.actions(plan))
        self.assertIn(("add", ".living/catalog.md"), self.actions(plan))
        self.assertFalse((self.ws / "value-check/log.md").exists())
        self.assertTrue((self.ws / ".living/catalog.md").is_file())

    def test_human_folders_and_setup_are_never_touched(self):
        for rel in ("decisions/2026-10-01-x.md", "proposals/2026-10-01-y.md", "projects/p.md"):
            (self.ws / rel).write_text("mine\n")
        (self.ws / "me/goals.md").write_text("my goals\n")
        self.make_old_hash_only("me/goals.md", "older\n")
        prof = (self.ws / ".living/profile.json").read_bytes()
        self.make_old("AGENTS.md", "old\n")
        L.upgrade(self.ws, apply=True)
        for rel in ("decisions/2026-10-01-x.md", "proposals/2026-10-01-y.md", "projects/p.md"):
            self.assertEqual((self.ws / rel).read_text(), "mine\n")
        self.assertEqual((self.ws / "me/goals.md").read_text(), "my goals\n")
        self.assertEqual((self.ws / ".living/profile.json").read_bytes(), prof)

    def test_routing_update_keeps_installed_module_rows(self):
        L.add_module(self.ws, "weekly-update", apply=True)
        r = self.ws / "CONTEXT-ROUTING.md"
        text = r.read_text()
        base = L.without_modules_block(text)
        old_base = base.replace("Start with the smallest route.", "Old wording.")
        r.write_text(old_base.rstrip("\n") + "\n\n" + L.modules_block(text))
        self.make_old_hash_only("CONTEXT-ROUTING.md", old_base)
        L.upgrade(self.ws, apply=True)
        after = r.read_text()
        self.assertIn("Start with the smallest route.", after)
        self.assertIn("<!-- module:weekly-update -->", after)
        self.assertEqual(L.doctor(self.ws)[0][0], "WARN", "no errors after upgrade")
        self.assertFalse([x for x in L.doctor(self.ws) if x[0] == "ERROR"])

    def test_module_files_and_rows_are_refreshed(self):
        L.add_module(self.ws, "staged-learning", apply=True)
        new_inbox = (self.ws / "lessons/inbox.md").read_text()
        self.make_old("lessons/inbox.md", "# old inbox\n", module="staged-learning")
        (self.ws / "lessons/active.md").write_text("## Active lessons\n\n- mine\n")
        r = self.ws / "CONTEXT-ROUTING.md"
        r.write_text("".join(l for l in r.read_text().splitlines(True) if "lessons/README.md" not in l))
        plan = L.upgrade(self.ws, apply=True)
        self.assertIn(("update", "lessons/inbox.md"), self.actions(plan))
        self.assertIn(("routing", "staged-learning"), self.actions(plan))
        self.assertEqual((self.ws / "lessons/inbox.md").read_text(), new_inbox)
        self.assertEqual((self.ws / "lessons/active.md").read_text(), "## Active lessons\n\n- mine\n")
        self.assertIn("`lessons/README.md` <!-- module:staged-learning -->", r.read_text())
        self.assertFalse([x for x in L.doctor(self.ws) if x[0] == "ERROR"])

    def test_failure_restores_everything(self):
        self.make_old("AGENTS.md", "old\n")
        L.add_module(self.ws, "staged-learning", apply=True)
        self.make_old("lessons/inbox.md", "# old inbox\n", module="staged-learning")
        before = snapshot(self.ws)
        with mock.patch.object(L, "write_json", side_effect=OSError("disk full (simulated)")):
            with self.assertRaises(OSError):
                L.upgrade(self.ws, apply=True)
        self.assertEqual(snapshot(self.ws), before)

    def test_lock_and_damaged_profile_are_refused(self):
        (self.ws / ".living/.lock").write_text("")
        with self.assertRaises(L.Refusal):
            L.upgrade(self.ws, apply=True)
        (self.ws / ".living/.lock").unlink()
        (self.ws / ".living/profile.json").write_text("{")
        with self.assertRaises(L.Refusal):
            L.upgrade(self.ws)


if __name__ == "__main__":
    unittest.main()

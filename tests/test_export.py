"""Exporting a workspace to one zip file, and restoring it on another computer."""
import json, os, sys, tempfile, unittest, zipfile
from unittest import mock
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


class TestExport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "manager", "de")
        L.add_module(self.ws, "weekly-update", apply=True)
        rel, _ = L.propose(self.ws, "new", "Erste Regel", "Nur ich schicke etwas an Kunden.", "Test", date="2026-10-24",
                           apply=True)
        L.review_tool().review(self.ws, rel, "approve", "Owner", date="2026-10-24")
        (self.ws / ".living/upgrade").mkdir()
        (self.ws / ".living/upgrade/AGENTS.md").write_text("x", encoding="utf-8")
        (self.ws / ".git").mkdir()
        (self.ws / ".git/config").write_text("x", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_plan_writes_nothing_and_apply_makes_one_zip(self):
        before = snapshot(self.ws)
        files = L.export(self.ws, self.base / "backup.zip")
        self.assertFalse((self.base / "backup.zip").exists())
        self.assertEqual(snapshot(self.ws), before)
        L.export(self.ws, self.base / "backup.zip", apply=True)
        names = zipfile.ZipFile(self.base / "backup.zip").namelist()
        self.assertEqual(sorted(names), sorted(files + ["EXPORT-README.txt", "EXPORT-FILES.txt"]))
        for left_out in (".living/local.json", ".living/upgrade/AGENTS.md", ".git/config"):
            self.assertNotIn(left_out, names)
        for kept in ("decisions/2026-10-24-erste-regel.md", ".claude/settings.json", "tools/guard.py",
                     ".living/manifest.json", "workflows/weekly-update/CONTEXT.md"):
            self.assertIn(kept, names)
        self.assertEqual(snapshot(self.ws), before, "export never changes the workspace")
        self.assertEqual([p.name for p in self.base.iterdir() if p.name.startswith(".living-export")], [])

    def test_refusals(self):
        for target in (self.ws / "inside.zip", self.base / "backup.tar", self.base / "missing/backup.zip"):
            with self.subTest(target=str(target)):
                with self.assertRaises(L.Refusal):
                    L.export(self.ws, target, apply=True)
        (self.base / "taken.zip").write_text("x", encoding="utf-8")
        with self.assertRaises(L.Refusal):
            L.export(self.ws, self.base / "taken.zip", apply=True)

    def test_restore_on_another_computer(self):
        L.export(self.ws, self.base / "backup.zip", apply=True)
        restored = self.base / "restored"
        zipfile.ZipFile(self.base / "backup.zip").extractall(restored)
        self.assertIn("INFO", [lvl for lvl, m in L.doctor(restored) if "local.json is missing" in m])
        plan = L.upgrade(restored)
        self.assertIn(("local", ".living/local.json"), {(a, r) for a, r, _, _ in plan})
        L.upgrade(restored, apply=True)
        folder = json.loads((restored / ".living/local.json").read_text(encoding="utf-8"))["product_folder"]
        self.assertTrue((Path(folder) / "tools/living.py").is_file())
        self.assertEqual(L.review_tool().current_decisions(restored), ["decisions/2026-10-24-erste-regel.md"])
        self.assertFalse([m for lvl, m in L.doctor(restored) if lvl == "ERROR"])
        self.assertEqual(L.format_upgrade_plan(L.upgrade(restored)), "Already up to date.")

    @unittest.skipIf(os.name == "nt", "creating links needs extra rights on Windows")
    def test_links_are_not_followed(self):
        (self.base / "secret.txt").write_text("outside", encoding="utf-8")
        (self.ws / "knowledge/link.txt").symlink_to(self.base / "secret.txt")
        self.assertNotIn("knowledge/link.txt", L.export(self.ws, self.base / "b.zip"))



class TestExportReview4(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "student", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def test_review_lock_is_left_out_and_blocks_a_half_way_export(self):
        (self.ws / ".review.lock").write_text("", encoding="utf-8")
        self.assertNotIn(".review.lock", L.export_files(self.ws))
        with self.assertRaises(L.Refusal):
            L.export(self.ws, self.base / "b.zip", apply=True)
        self.assertFalse((self.base / "b.zip").exists())

    @unittest.skipIf(os.name == "nt", "creating links needs extra rights on Windows")
    def test_a_file_swapped_for_a_link_is_refused(self):
        (self.base / "private.txt").write_text("private", encoding="utf-8")
        (self.ws / "knowledge/source.md").write_text("ok", encoding="utf-8")
        real = L.export_files

        def swap(ws):
            files = real(ws)
            (self.ws / "knowledge/source.md").unlink()
            (self.ws / "knowledge/source.md").symlink_to(self.base / "private.txt")
            return files

        with mock.patch.object(L, "export_files", swap):
            with self.assertRaises(L.Refusal):
                L.export(self.ws, self.base / "b.zip", apply=True)
        self.assertFalse((self.base / "b.zip").exists())

    def test_a_destination_that_appears_is_not_overwritten(self):
        import zipfile as zf
        real = zf.ZipFile.close

        def appear(self_zip):
            real(self_zip)
            (self.base / "b.zip").write_text("someone else's file", encoding="utf-8")

        with mock.patch.object(zf.ZipFile, "close", appear):
            with self.assertRaises(L.Refusal):
                L.export(self.ws, self.base / "b.zip", apply=True)
        self.assertEqual((self.base / "b.zip").read_text(encoding="utf-8"), "someone else's file")

if __name__ == "__main__":
    unittest.main()

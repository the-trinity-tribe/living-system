"""Health files: doctor --out, export-check, and the plain menu."""
import subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

run = lambda *a: subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), *a],
                                capture_output=True, text=True, encoding="utf-8")


class TestHealthFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "manager", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_check_accepts_a_real_export_and_names_problems(self):
        good = self.base / "good.zip"
        L.export(self.ws, good, apply=True)
        self.assertEqual(L.export_check(good)[0], [])
        bad = self.base / "bad.zip"
        with zipfile.ZipFile(good) as src, zipfile.ZipFile(bad, "w") as dst:
            for item in src.infolist():
                if item.filename not in ("AGENTS.md", "SYSTEM.md"):
                    dst.writestr(item, src.read(item))
        problems = L.export_check(bad)[0]
        self.assertIn("missing AGENTS.md", problems)
        self.assertTrue(any("installed file(s) missing" in p for p in problems))
        other = self.base / "other.zip"
        with zipfile.ZipFile(other, "w") as z:
            z.writestr("notes.txt", "x")
        self.assertIn("not a complete Living System export", L.export_check(other)[0][0])
        (self.base / "text.zip").write_text("not a zip", encoding="utf-8")
        with self.assertRaises(L.Refusal):
            L.export_check(self.base / "text.zip")
        self.assertEqual(run("export-check", str(good)).returncode, 0)
        self.assertEqual(run("export-check", str(bad)).returncode, 1)

    def test_export_check_sees_own_files_settings_manifest_and_links(self):  # sixth review, findings 2, 9-11
        L.add_module(self.ws, "careful-run", apply=True)
        (self.ws / "projects/mine.md").write_text("# Mine\n", encoding="utf-8")
        good = self.base / "good.zip"
        L.export(self.ws, good, apply=True)

        def variant(name, change):
            out = self.base / name
            with zipfile.ZipFile(good) as src, zipfile.ZipFile(out, "w") as dst:
                for item in src.infolist():
                    data = change(item, src.read(item))
                    if data is not None:
                        dst.writestr(item, data)
            return L.export_check(out)[0]
        self.assertIn("missing projects/mine.md", variant("a.zip", lambda i, d: None if i.filename == "projects/mine.md" else d))
        self.assertTrue(any("profile.json" in p for p in variant(
            "b.zip", lambda i, d: b"not json" if i.filename == ".living/profile.json" else d)))
        self.assertTrue(any("manifest" in p for p in variant(
            "c.zip", lambda i, d: b'{"files": {}, "modules": []}' if i.filename == ".living/manifest.json" else d)))

        def as_link(i, d):
            if i.filename == "AGENTS.md":
                i.external_attr = (0o120777 << 16)
                return b"/elsewhere"
            return d
        self.assertTrue(any("not a plain file inside: AGENTS.md" in p for p in variant("d.zip", as_link)))

    def test_doctor_report_is_saved_outside_only(self):
        out = self.base / "health.md"
        r = run("doctor", str(self.ws), "--out", str(out))
        self.assertIn("Saved", r.stdout)
        text = out.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(L.DOCTOR_MARK))
        self.assertIn("SYSTEM.md is not approved yet", text)
        self.assertEqual(run("doctor", str(self.ws), "--out", str(self.ws / "health.md")).returncode, 2)

    def test_menu_without_a_command(self):
        for args in ((), ("menu",)):
            with self.subTest(args=args):
                r = run(*args)
                self.assertEqual(r.returncode, 0)
                self.assertIn("What needs me?", r.stdout)


if __name__ == "__main__":
    unittest.main()

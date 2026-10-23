"""Focus mode, the handover capsule, and a handover note that is older than the work."""
import json, os, sys, tempfile, time, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class TestFocus(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "student", "de")

    def tearDown(self):
        self.tmp.cleanup()

    def test_on_and_off(self):
        self.assertIn("Undo: focus . off", L.focus(self.ws, "on"))
        self.assertTrue(json.loads((self.ws / ".living/profile.json").read_text(encoding="utf-8"))["focus"])
        self.assertIn("Focus mode: on", L.status(self.ws))
        L.focus(self.ws, "off")
        self.assertNotIn("Focus mode", L.status(self.ws))
        with self.assertRaises(L.Refusal):
            L.focus(self.ws, "maybe")
        L.focus(self.ws, "on")
        L.upgrade(self.ws, apply=True)
        self.assertTrue(json.loads((self.ws / ".living/profile.json").read_text(encoding="utf-8"))["focus"])

    def test_old_handover_note_is_pointed_out(self):
        note = self.ws / "handover/LATEST.md"
        write(note, "# Handover\n\n**Next step:** finish the essay outline\n")
        old = time.time() - 3 * 86400
        os.utime(note, (old, old))
        self.assertNotIn("changed after it", L.status(self.ws))
        write(self.ws / "projects/essay.md", "# Essay\n")
        self.assertIn("1 file(s) changed after it, e.g. projects/essay.md", L.status(self.ws))

    def test_capsule_fields_and_rules(self):
        self.assertIn("**Ziel**", (self.ws / "handover/LATEST.md").read_text(encoding="utf-8"))
        for lang in ("", "i18n/de/", "i18n/pl/"):
            text = (REPO / f"core/{lang}template/handover/LATEST.md").read_text(encoding="utf-8")
            self.assertEqual(text.count("**"), 14, lang)  # seven bold labels in every language
        self.assertIn("## 10a. Focus mode", (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

"""The personal work agreement: user-owned, private, read by the agent, added by upgrade."""
import json, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


class TestAgreement(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_language_gets_the_same_sections(self):
        counts = {}
        for lang, word in (("en", "What time saved is for"), ("de", "Wofür gewonnene Zeit da ist"),
                           ("pl", "Na co jest zaoszczędzony czas")):
            ws = L.init(self.base / lang, "professional", lang)
            text = (ws / L.AGREEMENT_FILE).read_text(encoding="utf-8")
            self.assertIn(word, text)
            counts[lang] = text.count("\n## ")
            self.assertIn("`me/agreement.md`", (ws / "CONTEXT-ROUTING.md").read_text(encoding="utf-8"))
        self.assertEqual(len(set(counts.values())), 1, counts)

    def test_private_for_employees_and_shown_in_agency(self):
        ws = L.init(self.base / "emp", "employee", "en")
        self.assertIn("me/", (ws / ".gitignore").read_text(encoding="utf-8"))
        self.assertIn(f"personal work agreement: {L.AGREEMENT_FILE}", L.agency(ws))

    def test_upgrade_adds_it_to_an_older_workspace_and_keeps_edits(self):
        ws = L.init(self.base / "old", "student", "en")
        (ws / L.AGREEMENT_FILE).unlink()  # a workspace made before the agreement existed: not in its manifest either
        manifest = json.loads((ws / ".living/manifest.json").read_text(encoding="utf-8"))
        del manifest["files"][L.AGREEMENT_FILE]
        (ws / ".living/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        L.upgrade(ws, apply=True)
        self.assertTrue((ws / L.AGREEMENT_FILE).is_file())
        (ws / L.AGREEMENT_FILE).write_text("# Mine\n\nShort answers.\n", encoding="utf-8")
        L.upgrade(ws, apply=True)
        self.assertEqual((ws / L.AGREEMENT_FILE).read_text(encoding="utf-8"), "# Mine\n\nShort answers.\n")

    def test_agent_rules(self):
        agents = (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Never add to the agreement yourself or guess things about the person", agents)
        self.assertIn("**Protected time.**", agents)


if __name__ == "__main__":
    unittest.main()

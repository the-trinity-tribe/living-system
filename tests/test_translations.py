"""Translated starter files (core/i18n/<language>/) stay structurally identical to the English ones."""
import re, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

LANGS = sorted(p.name for p in (REPO / "core/i18n").iterdir() if p.is_dir())
PROFILES = ("student", "professional", "employee", "manager")


def structure(text):
    """What tools and links depend on: front matter, markers, and code spans that are paths or commands."""
    front = re.match(r"---\n.*?\n---\n", text, re.S)
    spans = {re.sub(r"<[^>]+>", "<...>", s) for s in re.findall(r"`([^`]+)`", text)  # placeholders may be translated
             if "/" in s or s.endswith(".md") or s.startswith(("python3", "status:", "--")) or s.startswith("##")}
    markers = sorted(re.findall(r"<!-- [a-z:]+ -->", text))
    return front.group(0) if front else None, spans, markers


class TestTranslationFiles(unittest.TestCase):
    def test_german_and_polish_exist(self):
        self.assertTrue({"de", "pl"} <= set(LANGS))

    def test_every_translation_has_an_english_original_and_the_same_structure(self):
        for lang in LANGS:
            base = REPO / "core/i18n" / lang
            for p in sorted(base.rglob("*")):
                if not p.is_file():
                    continue
                rel = p.relative_to(base)
                with self.subTest(lang=lang, file=rel.as_posix()):
                    self.assertNotIn(p.name, L.NOT_TRANSLATED, "agent rule files stay English")
                    english = REPO / "core" / rel
                    self.assertTrue(english.is_file(), f"no English original for {rel.as_posix()}")
                    front, spans, markers = structure(p.read_text(encoding="utf-8"))
                    en_front, en_spans, en_markers = structure(english.read_text(encoding="utf-8"))
                    self.assertEqual((front, markers), (en_front, en_markers))
                    self.assertEqual(en_spans - spans, set(), "every path, command and heading the English names")


class TestTranslatedWorkspaces(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_profile_in_every_language(self):
        english = {p: L.init(self.base / f"en-{p}", p, "en") for p in PROFILES}
        for lang in LANGS + ["de-AT"]:
            for profile in PROFILES:
                with self.subTest(lang=lang, profile=profile):
                    ws = L.init(self.base / f"{lang}-{profile}", profile, lang)
                    self.assertNotEqual((ws / "README.md").read_text(encoding="utf-8"),
                                        (english[profile] / "README.md").read_text(encoding="utf-8"))
                    for f in ("AGENTS.md", "CLAUDE.md"):
                        self.assertEqual((ws / f).read_bytes(), (english[profile] / f).read_bytes())
                    self.assertEqual(L.review_tool().check(ws), [])
                    self.assertEqual([lvl for lvl, _ in L.doctor(ws)], ["WARN", "WARN"])
                    self.assertEqual(L.format_upgrade_plan(L.upgrade(ws)), "Already up to date.")
                    counts, unscored = L.value_score(ws)
                    self.assertEqual(unscored, {"before": 5, "after": 5})
                    self.assertIsNone(L.handover_next_step(ws))

    def test_unknown_language_gets_english_files(self):
        ws = L.init(self.base / "fr", "student", "fr")
        en = L.init(self.base / "en", "student", "en")
        self.assertEqual((ws / "README.md").read_bytes(), (en / "README.md").read_bytes())

    def test_scores_and_next_steps_in_german_and_polish(self):
        ws = L.init(self.base / "de", "student", "de")
        (ws / "value-check/questions.md").write_text(
            "| # | Frage | Vorher | Nachher |\n| --- | --- | --- | --- |\n"
            "| 1 | a | `erfunden` | richtig |\n| 2 | b | weiß nicht | richtig |\n", encoding="utf-8", newline="\n")
        counts, _ = L.value_score(ws)
        self.assertEqual((counts["before"]["made up"], counts["before"]["don't know"], counts["after"]["right"]), (1, 1, 2))
        (ws / "value-check/questions.md").write_text(
            "| # | Pytanie | Przed | Po |\n| --- | --- | --- | --- |\n| 1 | a | źle | dobrze |\n| 2 | b | zmyślone | nie wiem |\n",
            encoding="utf-8", newline="\n")
        counts, _ = L.value_score(ws)
        self.assertEqual((counts["before"]["wrong"], counts["before"]["made up"], counts["after"]["right"],
                          counts["after"]["don't know"]), (1, 1, 1, 1))
        for text, step in (("- **Nächster Schritt für dich:** Entwurf prüfen\n", "Entwurf prüfen"),
                           ("## Następny krok dla ciebie\n\n- Sprawdź szkic\n", "Sprawdź szkic")):
            (ws / "handover/LATEST.md").write_text("# Übergabe\n\n" + text, encoding="utf-8", newline="\n")
            self.assertEqual(L.handover_next_step(ws), step)


if __name__ == "__main__":
    unittest.main()

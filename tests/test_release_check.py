"""The pre-release scan finds what must never be published, and stays quiet on the real repository."""
import sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import release_check as RC

PRIVATE_NAME = "TTT" + "-System"
MAIL = "someone" + "@" + "realmail.de"
HOME = "/" + "home/someone/projects/"
BOT = "noreply" + "@" + "anthropic.com"


class TestReleaseCheck(unittest.TestCase):
    def scan(self, files, messages=()):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for rel, text in files.items():
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(text, encoding="utf-8", newline="\n")
                paths.append(root / rel)
            return RC.scan(root, paths, list(messages))

    def levels(self, findings):
        return sorted({(lvl, where.split(":")[0]) for lvl, where, _ in findings})

    def test_finds_what_must_not_be_published(self):
        key = "sk-" + "a" * 24
        found = self.scan({
            "README.md": f"Built from {PRIVATE_NAME}.\n",
            "docs/a.md": f"Contact me at {MAIL}\n",
            "tools/x.py": f'API_KEY = "{key}"\n',
            "core/template/SYSTEM.md": "Maya Chen approves everything.\n",
            "modules/m/README.md": f"Run it from {HOME}\n",
        }, messages=[("abc12345", f"feat: x\n\nCo-Authored-By: Claude <{BOT}>")])
        self.assertEqual(self.levels(found), [("ERROR", "README.md"), ("ERROR", "commit abc12345"),
                                              ("ERROR", "core/template/SYSTEM.md"), ("ERROR", "docs/a.md"),
                                              ("ERROR", "modules/m/README.md"), ("ERROR", "tools/x.py")])

    def test_finds_ordinary_windows_paths_config_secrets_key_files_and_test_files(self):
        value = "LongRealistic" + "SecretValue1"
        key_header = "-----BEGIN PRIVATE " + "KEY-----"
        found = self.scan({
            "docs/win.md": "Saved in C:" + "\\Users\\Alice\\Documents\\private\n",
            "config/settings.json": '{"pass' + 'word": "' + value + '"}\n',
            ".env": "API" + "_KEY=" + value + "\n",
            "certs/private.pem": key_header + "\nabc\n",
            "tests/live.py": 'TOKEN = "' + "sk-" + "b" * 30 + '"\n',
        })
        self.assertEqual(self.levels(found), [("ERROR", ".env"), ("ERROR", "certs/private.pem"),
                                              ("ERROR", "config/settings.json"), ("ERROR", "docs/win.md"),
                                              ("ERROR", "tests/live.py")])

    def test_overclaims_warn_unless_the_line_says_what_is_not_promised(self):
        found = self.scan({"site/index.html": "<p>A secure, compliant system.</p>\n<p>It is not a secure vault.</p>\n"})
        self.assertEqual([(lvl, where) for lvl, where, _ in found], [("WARN", "site/index.html:1")])

    def test_allowed_examples_pass(self):
        found = self.scan({"docs/a.md": "Write to person" + "@" + "example.com. The demo names Riverside.\n"})
        self.assertEqual(found, [])

    def test_real_repository_has_no_errors(self):
        errors = [f for f in RC.scan(REPO) if f[0] == "ERROR"]
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()

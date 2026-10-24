"""The careful-run module and its checkpoint: pause, then resume only after seeing what changed."""
import subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

CARD = "workflows/careful-run/runs/2026-10-24-site.md"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class TestCarefulRun(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")
        L.add_module(self.ws, "careful-run", apply=True)
        template = (self.ws / "workflows/careful-run/references/run-card.md").read_text(encoding="utf-8")
        write(self.ws / CARD, template.replace("  - `<path>`", "  - `projects/site.md`\n  - `projects/new.md`"))
        write(self.ws / "projects/site.md", "# Site\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_installs_with_six_stages_and_stays_clean(self):
        for stage in ("01-frame", "02-plan", "03-make", "04-check", "05-verify", "06-hand-back"):
            text = (self.ws / f"workflows/careful-run/{stage}/CONTEXT.md").read_text(encoding="utf-8")
            self.assertLess(len(text.splitlines()), 80)
            for heading in ("## Inputs", "## Process", "## Outputs", "## Checkpoint"):
                self.assertIn(heading, text)
        self.assertFalse([lvl for lvl, m in L.doctor(self.ws) if lvl == "ERROR"])

    def test_record_then_compare(self):
        problems, message = L.checkpoint(self.ws, CARD, record=True)
        self.assertIn("Checkpoint recorded for 2 file(s); not there yet: projects/new.md", message)
        self.assertEqual(L.checkpoint(self.ws, CARD)[0], [])
        write(self.ws / "projects/site.md", "# Site\n\nchanged\n")
        write(self.ws / "projects/new.md", "# New\n")
        problems, _ = L.checkpoint(self.ws, CARD)
        self.assertEqual(problems, ["projects/site.md: changed since the checkpoint",
                                    "projects/new.md: created since the checkpoint"])
        L.checkpoint(self.ws, CARD, record=True)  # recording again replaces the section
        text = (self.ws / CARD).read_text(encoding="utf-8")
        self.assertEqual(text.count(L.CHECKPOINT_HEAD), 1)
        (self.ws / "projects/site.md").unlink()
        self.assertEqual(L.checkpoint(self.ws, CARD)[0], ["projects/site.md: missing now"])

    def test_crlf_is_not_a_change_and_refusals(self):
        L.checkpoint(self.ws, CARD, record=True)
        site = self.ws / "projects/site.md"
        site.write_bytes(site.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(L.checkpoint(self.ws, CARD)[0], [])
        write(self.ws / "workflows/careful-run/runs/fresh.md", "# Run card\n\nFiles in scope:\n  - `x.md`\n")
        for card, kw in ((CARD.replace("2026", "1999"), {}), ("../outside.md", {}), ("projects/site.md", {}),
                         ("workflows/careful-run/runs/fresh.md", {})):
            with self.subTest(card=card), self.assertRaises(L.Refusal):
                L.checkpoint(self.ws, card, **kw)
        write(self.ws / "workflows/careful-run/runs/bad.md", "Files in scope:\n  - `../../etc/passwd`\n")
        with self.assertRaises(L.Refusal):
            L.checkpoint(self.ws, "workflows/careful-run/runs/bad.md", record=True)

    def test_command_line_exit_codes(self):
        run = lambda *a: subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "checkpoint", str(self.ws),
                                         CARD, *a], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run("--record").returncode, 0)
        self.assertEqual(run().returncode, 0)
        write(self.ws / "projects/site.md", "# Site\n\nchanged\n")
        changed = run()
        self.assertEqual(changed.returncode, 1)
        self.assertIn("re-read these before continuing", changed.stdout)


if __name__ == "__main__":
    unittest.main()

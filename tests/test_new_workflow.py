"""Generating a staged (ICM-style) workflow folder in a workspace."""
import sys, tempfile, unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


class TestNewWorkflow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "manager", "en")
        self.before = snapshot(self.ws)

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_run_writes_nothing(self):
        paths = L.new_workflow(self.ws, "campaign", ["research", "draft", "review"])
        self.assertIn("workflows/campaign/02-draft/CONTEXT.md", paths)
        self.assertEqual(snapshot(self.ws), self.before)

    def test_structure_and_stage_contracts(self):
        L.new_workflow(self.ws, "campaign", ["research", "draft", "review"], "A launch post plan", apply=True)
        wf = self.ws / "workflows/campaign"
        self.assertEqual(sorted(p.name for p in wf.iterdir()),
                         ["01-research", "02-draft", "03-review", "CONTEXT.md", "references"])
        root = (wf / "CONTEXT.md").read_text()
        for h in ("## Stages", "## Decisions that apply", "## Never do"):
            self.assertIn(h, root)
        self.assertIn("Goal: A launch post plan", root)
        for i, stage in enumerate(("01-research", "02-draft", "03-review")):
            text = (wf / stage / "CONTEXT.md").read_text()
            self.assertLess(len(text.splitlines()), 80)
            for h in ("## Inputs", "## Process", "## Outputs", "## Checkpoint"):
                self.assertIn(h, text)
            self.assertTrue((wf / stage / "output/.gitkeep").is_file())
            if i:
                self.assertIn(f"`{('01-research', '02-draft')[i - 1]}/output/`", text)
        self.assertFalse(list(wf.rglob("AGENTS.md")) + list(wf.rglob("CLAUDE.md")))
        self.assertIn(L.FILL, (wf / "02-draft/CONTEXT.md").read_text())

    def test_refusals_write_nothing(self):
        (self.ws / "workflows/taken").mkdir()
        cases = [("taken", ["a"]), ("../escape", ["a"]), ("ok", []), ("ok", ["a", "a"]),
                 ("ok", ["Bad Name"]), ("ok", [str(i) for i in range(10)])]
        before = snapshot(self.ws)
        for name, stages in cases:
            with self.subTest(name=name, stages=stages):
                with self.assertRaises(L.Refusal):
                    L.new_workflow(self.ws, name, stages, apply=True)
        with self.assertRaises(L.Refusal):
            L.new_workflow(self.ws, "ok", ["a"], goal="two\nlines", apply=True)
        self.assertEqual(snapshot(self.ws), before)
        self.assertEqual(sorted(p.name for p in (self.ws / "workflows").iterdir()), [".gitkeep", "taken"])

    def test_failure_leaves_no_half_made_folder(self):
        with mock.patch.object(Path, "write_text", side_effect=OSError("disk full (simulated)")):
            with self.assertRaises(OSError):
                L.new_workflow(self.ws, "campaign", ["a", "b"], apply=True)
        self.assertEqual(snapshot(self.ws), self.before)
        self.assertEqual([p.name for p in (self.ws / "workflows").iterdir()], [".gitkeep"])

    def test_not_a_workspace(self):
        with self.assertRaises(L.Refusal):
            L.new_workflow(Path(self.tmp.name), "x", ["a"])


if __name__ == "__main__":
    unittest.main()

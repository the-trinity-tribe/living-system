"""Optional modules: listing, planning, adding and removing them safely."""
import json, re, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

FEATURE_HEADINGS = re.findall(r"^## (.+)$", (REPO / "docs/features/_template.md").read_text(), re.M)


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


def make_module(root, mid, files, requires=(), routing=None, **extra):
    d = Path(root) / mid
    for rel, text in files.items():
        (d / "files" / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / "files" / rel).write_text(text)
    meta = {"id": mid, "version": "0.1.0", "kind": "workflow", "summary": f"{mid} summary",
            "requires": list(requires), "routing": routing if routing is not None else [[f"{mid} need", next(iter(files))]],
            "needs_approval": [], "signals": [f"{mid} signal"], **extra}
    (d / "module.json").write_text(json.dumps(meta))
    return d


class ModuleCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "professional", "en")
        self.before = snapshot(self.ws)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        r = subprocess.run([sys.executable, "-B", str(self.ws / "tools/review.py"), "--root", str(self.ws), "check"],
                           capture_output=True, text=True)
        return r.stdout.strip()


class TestShippedModules(unittest.TestCase):
    def test_every_module_loads_and_is_documented(self):
        ids = [d.name for d in sorted(L.MODULES.iterdir()) if (d / "module.json").is_file()]
        self.assertGreaterEqual(len(ids), 3)
        self.assertEqual(len(FEATURE_HEADINGS), 10)
        for mid in ids:
            with self.subTest(module=mid):
                m = L.load_module(mid)
                readme = (m["dir"] / "README.md").read_text()
                self.assertEqual(re.findall(r"^## (.+)$", readme, re.M), FEATURE_HEADINGS)
                self.assertIn(f"Module id: `{mid}`", readme)
                self.assertNotIn("Moss", readme + "".join((m["dir"] / "files" / f).read_text() for f in m["files"]))

    def test_workflow_stage_files_stay_short_and_complete(self):
        for ctx in L.MODULES.glob("*/files/workflows/*/[0-9][0-9]-*/CONTEXT.md"):
            with self.subTest(stage=str(ctx.relative_to(L.MODULES))):
                text = ctx.read_text()
                self.assertLess(len(text.splitlines()), 80)
                for h in ("## Inputs", "## Process", "## Outputs", "## Checkpoint"):
                    self.assertIn(h, text)

    def test_every_module_installs_and_removes_cleanly_together(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = L.init(Path(tmp) / "ws", "manager", "de")
            before = snapshot(ws)
            ids = [d.name for d in sorted(L.MODULES.iterdir()) if (d / "module.json").is_file()]
            for mid in ids:
                L.add_module(ws, mid, apply=True)
            r = subprocess.run([sys.executable, "-B", str(ws / "tools/review.py"), "--root", str(ws), "check"],
                               capture_output=True, text=True)
            self.assertEqual(r.stdout.strip(), "ok")
            for mid in reversed(ids):
                L.remove_module(ws, mid, apply=True)
            self.assertEqual(snapshot(ws), before)


class TestAddRemove(ModuleCase):
    def test_dry_run_writes_nothing(self):
        order = L.add_module(self.ws, "weekly-update")
        self.assertEqual([m["id"] for m in order], ["weekly-update"])
        self.assertEqual(snapshot(self.ws), self.before)

    def test_apply_installs_files_routing_and_manifest(self):
        L.add_module(self.ws, "weekly-update", apply=True)
        self.assertTrue((self.ws / "workflows/weekly-update/02-draft/CONTEXT.md").is_file())
        routing = (self.ws / "CONTEXT-ROUTING.md").read_text()
        self.assertIn("## Installed modules", routing)
        self.assertIn("`workflows/weekly-update/CONTEXT.md` <!-- module:weekly-update --> |", routing)
        entry = json.loads((self.ws / ".living/manifest.json").read_text())["modules"]["weekly-update"]
        self.assertEqual(entry["files"]["workflows/weekly-update/CONTEXT.md"],
                         L.sha256(self.ws / "workflows/weekly-update/CONTEXT.md"))
        self.assertEqual(self.check(), "ok")
        self.assertIn("[installed] weekly-update", L.list_modules(ws=self.ws))

    def test_add_then_remove_restores_workspace_exactly(self):
        L.add_module(self.ws, "meeting-notes", apply=True)
        L.add_module(self.ws, "staged-learning", apply=True)
        L.remove_module(self.ws, "meeting-notes", apply=True)
        L.remove_module(self.ws, "staged-learning", apply=True)
        self.assertEqual(snapshot(self.ws), self.before)

    def test_remove_keeps_edited_files_and_dry_run_changes_nothing(self):
        L.add_module(self.ws, "staged-learning", apply=True)
        (self.ws / "lessons/active.md").write_text("# Active lessons\n\n## Active lessons\n\n- mine\n")
        mid = snapshot(self.ws)
        delete, keep, missing = L.remove_module(self.ws, "staged-learning")
        self.assertEqual(snapshot(self.ws), mid)
        self.assertEqual(keep, ["lessons/active.md"])
        L.remove_module(self.ws, "staged-learning", apply=True)
        self.assertEqual((self.ws / "lessons/active.md").read_text().splitlines()[-1], "- mine")
        self.assertFalse((self.ws / "lessons/inbox.md").exists())
        self.assertNotIn("modules", json.loads((self.ws / ".living/manifest.json").read_text()))

    def test_remove_never_touches_human_folders(self):
        L.add_module(self.ws, "meeting-notes", apply=True)
        (self.ws / "proposals/2026-10-23-x.md").write_text("mine")
        L.remove_module(self.ws, "meeting-notes", apply=True)
        self.assertEqual((self.ws / "proposals/2026-10-23-x.md").read_text(), "mine")

    def test_existing_file_blocks_install(self):
        (self.ws / "workflows/weekly-update").mkdir()
        (self.ws / "workflows/weekly-update/CONTEXT.md").write_text("mine")
        before = snapshot(self.ws)
        with self.assertRaises(L.Refusal):
            L.add_module(self.ws, "weekly-update", apply=True)
        self.assertEqual(snapshot(self.ws), before)

    def test_failed_install_rolls_back(self):
        with mock.patch.object(L, "write_json", side_effect=OSError("disk full (simulated)")):
            with self.assertRaises(OSError):
                L.add_module(self.ws, "weekly-update", apply=True)
        self.assertEqual(snapshot(self.ws), self.before)
        self.assertFalse((self.ws / "workflows/weekly-update").exists())

    def test_twice_and_unknown_are_refused(self):
        L.add_module(self.ws, "weekly-update", apply=True)
        for call in (lambda: L.add_module(self.ws, "weekly-update"),
                     lambda: L.add_module(self.ws, "no-such-module"),
                     lambda: L.add_module(self.ws, "../core"),
                     lambda: L.remove_module(self.ws, "meeting-notes"),
                     lambda: L.add_module(self.base, "weekly-update")):
            with self.assertRaises(L.Refusal):
                call()


class TestDependenciesAndValidation(ModuleCase):
    def setUp(self):
        super().setUp()
        self.mods = self.base / "mods"
        make_module(self.mods, "base", {"workflows/base/CONTEXT.md": "base\n"})
        make_module(self.mods, "top", {"workflows/top/CONTEXT.md": "top\n"}, requires=["base"])

    def test_requirements_install_first_and_block_removal(self):
        order = L.add_module(self.ws, "top", apply=True, root=self.mods)
        self.assertEqual([m["id"] for m in order], ["base", "top"])
        self.assertIn("(required by top)", L.format_add_plan(order, "top"))
        with self.assertRaises(L.Refusal):
            L.remove_module(self.ws, "base")
        L.remove_module(self.ws, "top", apply=True)
        L.remove_module(self.ws, "base", apply=True)
        self.assertEqual(snapshot(self.ws), self.before)

    def test_unselected_modules_are_not_installed(self):
        L.add_module(self.ws, "base", apply=True, root=self.mods)
        self.assertFalse((self.ws / "workflows/top").exists())

    def test_dependency_loop_refused(self):
        make_module(self.mods, "a", {"workflows/a/CONTEXT.md": "a\n"}, requires=["b"])
        make_module(self.mods, "b", {"workflows/b/CONTEXT.md": "b\n"}, requires=["a"])
        with self.assertRaises(L.Refusal):
            L.add_module(self.ws, "a", root=self.mods)

    def test_module_may_not_ship_into_owned_places(self):
        bad = {
            "dec": {"decisions/2026-01-01-x.md": "x"},
            "prop": {"proposals/x.md": "x"},
            "nested": {"workflows/n/AGENTS.md": "x"},
            "claude": {"workflows/n/CLAUDE.md": "x"},
            "routing": {"CONTEXT-ROUTING.md": "x"},
            "system": {"SYSTEM.md": "x"},
            "tool": {"tools/review.py": "x"},
        }
        for mid, files in bad.items():
            with self.subTest(module=mid):
                make_module(self.mods, mid, files)
                with self.assertRaises(L.Refusal):
                    L.add_module(self.ws, mid, root=self.mods)
        self.assertEqual(snapshot(self.ws), self.before)

    def test_routing_must_point_at_own_file_and_stay_one_cell(self):
        make_module(self.mods, "elsewhere", {"workflows/e/CONTEXT.md": "e\n"}, routing=[["need", "AGENTS.md"]])
        make_module(self.mods, "pipe", {"workflows/p/CONTEXT.md": "p\n"}, routing=[["a | b", "workflows/p/CONTEXT.md"]])
        for mid in ("elsewhere", "pipe"):
            with self.assertRaises(L.Refusal):
                L.load_module(mid, self.mods)


class TestCLI(ModuleCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), *args],
                              capture_output=True, text=True)

    def test_plan_apply_and_refusal_codes(self):
        r = self.run_cli("add", str(self.ws), "weekly-update")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Nothing was written", r.stdout)
        self.assertEqual(snapshot(self.ws), self.before)
        self.assertEqual(self.run_cli("add", str(self.ws), "weekly-update", "--apply").returncode, 0)
        r = self.run_cli("add", str(self.ws), "weekly-update", "--apply")
        self.assertEqual(r.returncode, 2)
        self.assertIn("REFUSED", r.stderr)
        r = self.run_cli("modules", "--workspace", str(self.ws))
        self.assertIn("may help when you mention", r.stdout)
        self.assertIn("[installed] weekly-update", r.stdout)


if __name__ == "__main__":
    unittest.main()

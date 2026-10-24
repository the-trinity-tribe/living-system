"""Every shipped module installs cleanly, passes doctor, and removes without leftovers."""
import sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

IDS = [d.name for d in sorted(L.MODULES.iterdir()) if (d / "module.json").is_file()]


class TestEveryModule(unittest.TestCase):
    def test_install_doctor_remove(self):
        for mid in IDS:
            with self.subTest(module=mid), tempfile.TemporaryDirectory() as tmp:
                ws = L.init(Path(tmp) / "ws", "professional", "en")
                before = {p.relative_to(ws).as_posix() for p in ws.rglob("*") if p.is_file()}
                L.add_module(ws, mid, apply=True)
                self.assertEqual([m for lvl, m in L.doctor(ws) if lvl == "ERROR"], [])
                for ctx in (ws / "workflows" / mid).rglob("CONTEXT.md") if (ws / "workflows" / mid).is_dir() else []:
                    self.assertLess(len(ctx.read_text(encoding="utf-8").splitlines()), 80)
                if (ws / "workflows" / mid).is_dir():
                    self.assertNotIn("<fill in:", "".join(p.read_text(encoding="utf-8")
                                                          for p in (ws / "workflows" / mid).rglob("*.md")))
                L.remove_module(ws, mid, apply=True)
                after = {p.relative_to(ws).as_posix() for p in ws.rglob("*") if p.is_file()}
                self.assertEqual(after - before, set())

    def test_new_modules_are_there(self):
        for mid in ("careful-run", "work-audit", "research-review", "client-intake", "content-prep"):
            self.assertIn(mid, IDS)


if __name__ == "__main__":
    unittest.main()

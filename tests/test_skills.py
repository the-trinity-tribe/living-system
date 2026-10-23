"""Shared skills: one source in core/skills, copied for Claude Code (.claude/skills) and Codex (.agents/skills)."""
import re, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

SKILLS = sorted(p.parent.name for p in (REPO / "core/skills").glob("*/SKILL.md"))


class TestSkills(unittest.TestCase):
    def test_sources_are_well_formed(self):
        self.assertGreaterEqual(len(SKILLS), 4)
        agents = (REPO / "core/template/AGENTS.md").read_text(encoding="utf-8")
        for name in SKILLS:
            with self.subTest(skill=name):
                text = (REPO / "core/skills" / name / "SKILL.md").read_text(encoding="utf-8")
                front = re.match(r"---\n(.*?)\n---\n", text, re.S)
                self.assertIsNotNone(front, "front matter must open the file")
                fields = dict(line.split(": ", 1) for line in front.group(1).splitlines())
                self.assertEqual(set(fields), {"name", "description"})
                self.assertEqual(fields["name"], name)
                self.assertRegex(name, r"^[a-z0-9-]+$")
                self.assertLess(len(fields["description"]), 1536)
                self.assertLess(len(text.splitlines()), 500)
                for section in re.findall(r"section (\d+[a-z]?)", text):
                    self.assertRegex(agents, rf"(?m)^#+ {section}\. ", f"{name} cites missing AGENTS.md section {section}")

    def test_init_puts_the_same_skill_in_both_places(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = L.init(Path(tmp) / "ws", "employee", "pl")
            for name in SKILLS:
                src = (REPO / "core/skills" / name / "SKILL.md").read_bytes()
                for place in (".claude/skills", ".agents/skills"):
                    self.assertEqual((ws / place / name / "SKILL.md").read_bytes(), src)
            self.assertEqual([lvl for lvl, _ in L.doctor(ws)], ["WARN", "WARN"])
            self.assertEqual(L.format_upgrade_plan(L.upgrade(ws)), "Already up to date.")

    def test_upgrade_brings_skills_to_an_older_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = L.init(Path(tmp) / "ws", "student", "en")
            import json, shutil
            m = json.loads((ws / ".living/manifest.json").read_text(encoding="utf-8"))
            for place in (".claude/skills", ".agents/skills"):
                shutil.rmtree(ws / place)
                for k in [k for k in m["files"] if k.startswith(place)]:
                    del m["files"][k]
            (ws / ".living/manifest.json").write_text(json.dumps(m), encoding="utf-8")
            L.upgrade(ws, apply=True)
            self.assertTrue((ws / ".agents/skills/first-decision/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()

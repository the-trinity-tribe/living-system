"""Regression tests for the sixth code review (checkpoint, export-check, doctor, onboarding, modules)."""
import os, sys, tempfile, time, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R

CARD = "workflows/careful-run/runs/site.md"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class TestCheckpoint(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")
        L.add_module(self.ws, "careful-run", apply=True)
        write(self.ws / "projects/a.md", "A\n")
        write(self.ws / "projects/b.md", "B\n")

    def tearDown(self):
        self.tmp.cleanup()

    def card(self, files, extra=""):
        write(self.ws / CARD, "# Run card\n\n## Scope\n\n- Files in scope:\n" + files + "\n## Notes\n\nn\n" + extra)

    def test_sections_after_the_checkpoint_survive(self):  # finding 3
        self.card("  - `projects/a.md`\n")
        L.checkpoint(self.ws, CARD, record=True)
        path = self.ws / CARD
        write(path, path.read_text(encoding="utf-8") + "\n## Human feedback\n\nKeep this.\n")
        L.checkpoint(self.ws, CARD, record=True)
        text = path.read_text(encoding="utf-8")
        self.assertIn("## Human feedback\n\nKeep this.", text)
        self.assertEqual(text.count(L.CHECKPOINT_HEAD), 1)

    def test_a_file_dropped_from_scope_is_reported(self):  # finding 5
        self.card("  - `projects/a.md`\n  - `projects/b.md`\n")
        L.checkpoint(self.ws, CARD, record=True)
        text = (self.ws / CARD).read_text(encoding="utf-8").replace("  - `projects/b.md`\n", "", 1)
        write(self.ws / CARD, text)
        self.assertEqual(L.checkpoint(self.ws, CARD)[0], ["projects/b.md: in the checkpoint, but no longer listed in scope"])

    def test_blank_lines_inside_the_scope_list(self):  # finding 6
        self.card("  - `projects/a.md`\n\n  - `projects/b.md`\n")
        self.assertIn("2 file(s)", L.checkpoint(self.ws, CARD, record=True)[1])

    def test_binary_files_are_compared_byte_for_byte(self):  # finding 7
        (self.ws / "projects/logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00data")
        self.card("  - `projects/logo.png`\n")
        L.checkpoint(self.ws, CARD, record=True)
        (self.ws / "projects/logo.png").write_bytes(b"\x89PNG\n\x1a\n\x00data")
        self.assertEqual(L.checkpoint(self.ws, CARD)[0], ["projects/logo.png: changed since the checkpoint"])

    @unittest.skipIf(os.name == "nt", "links need extra rights on Windows")
    def test_linked_scope_files_are_refused(self):  # finding 8
        (self.ws / "projects/link.md").symlink_to(self.ws / "projects/a.md")
        self.card("  - `projects/link.md`\n")
        with self.assertRaises(L.Refusal):
            L.checkpoint(self.ws, CARD, record=True)

    def test_the_card_itself_is_refused(self):  # finding 15
        self.card(f"  - `{CARD}`\n")
        with self.assertRaises(L.Refusal):
            L.checkpoint(self.ws, CARD, record=True)


class TestDoctorAndOnboarding(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.org = L.init(self.base / "org", "manager", "en", team=True)
        self.ws = L.init(self.base / "ws", "employee", "en")
        L.link(self.ws, self.org, "sales")

    def tearDown(self):
        self.tmp.cleanup()

    def test_reports_are_not_saved_into_the_company_workspace(self):  # finding 1
        with self.assertRaises(L.Refusal):
            L.write_handbook(self.ws, self.org / "roles/sales/knowledge/health.md", "x", L.DOCTOR_MARK, "health report")

    def test_a_damaged_decision_does_not_stop_doctor(self):  # finding 12
        write(self.ws / "decisions/2026-10-01-bad.md", "no front matter\n")
        self.assertTrue(L.doctor(self.ws))

    def test_references_outside_the_workspace_and_md_folders(self):  # findings 17 and 19
        write(self.ws / "knowledge/x.md", "# X\n\nSee ../../org/decisions/ref.md and `C:/org/decisions/other.md`.\n")
        (self.ws / "knowledge/archive.md").mkdir()
        self.assertFalse(any("does not exist" in m for _, m in L.knowledge_upkeep(self.ws, R)))

    def test_bom_roles_line_still_filters(self):  # finding 18
        (self.org / "workflows/payroll").mkdir(parents=True)
        (self.org / "workflows/payroll/CONTEXT.md").write_bytes("\ufeffRoles: finance\n# Payroll\n".encode("utf-8"))
        self.assertNotIn("company:workflows/payroll/CONTEXT.md", [i for _, i, *_ in L.onboarding_items(self.ws)])

    def test_changes_later_the_same_day_are_noticed(self):  # finding 16
        note = self.ws / "handover/LATEST.md"
        write(note, "# Handover\n\n**Next step:** call the printer\n")
        earlier = time.time() - 600
        os.utime(note, (earlier, earlier))
        write(self.ws / "projects/new.md", "# New\n")
        self.assertIn("changed after it", L.status(self.ws))


class TestModuleNames(unittest.TestCase):
    def test_outputs_are_named_per_run_client_or_piece(self):  # findings 13 and 14
        checks = {"careful-run": "<card-name>-check-<round>", "client-intake": "the `<client-code>` file",
                  "content-prep": "<piece-name>-check-<round>", "research-review": "<question-name>", "work-audit": "<audit-name>"}
        for mid, marker in checks.items():
            text = "".join(p.read_text(encoding="utf-8") for p in (REPO / "modules" / mid).rglob("CONTEXT.md"))
            with self.subTest(module=mid):
                self.assertIn(marker, text)
                self.assertNotIn("newest file in `", text.replace("the newest `<card-name>", ""))

    def test_roadmap_names_real_commands(self):  # finding 20
        text = (REPO / "docs/roadmap.md").read_text(encoding="utf-8")
        self.assertNotIn("run-check", text)
        self.assertNotIn("export --check", text)


if __name__ == "__main__":
    unittest.main()

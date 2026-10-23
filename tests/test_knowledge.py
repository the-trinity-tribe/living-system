"""The knowledge-inbox module: staged knowledge, last_verified dates and re-check reminders."""
import datetime, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

TODAY = datetime.date.today()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def knowledge(days_ago, topic="Invoicing"):
    date = (TODAY - datetime.timedelta(days=days_ago)).isoformat()
    return f"---\nlast_verified: {date}\nsource: an article\n---\n\n# {topic}\n\nFacts.\n"


class TestKnowledgeInbox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")
        for f in ("SYSTEM.md", "PRINCIPLES.md"):
            p = self.ws / f
            write(p, p.read_text(encoding="utf-8").replace("status: draft", "status: approved", 1))
        L.add_module(self.ws, "knowledge-inbox", apply=True)

    def tearDown(self):
        self.tmp.cleanup()

    def messages(self):
        return [(lvl, msg) for lvl, msg in L.doctor(self.ws)]

    def test_fresh_install_is_clean_and_routed(self):
        self.assertEqual(self.messages(), [])
        routing = (self.ws / "CONTEXT-ROUTING.md").read_text(encoding="utf-8")
        self.assertIn("`knowledge/README.md` <!-- module:knowledge-inbox -->", routing)
        self.assertIn("`knowledge/inbox.md` <!-- module:knowledge-inbox -->", routing)

    def test_recent_file_is_fine_and_old_file_is_flagged(self):
        write(self.ws / "knowledge/invoicing.md", knowledge(10))
        write(self.ws / "knowledge/tax/vat.md", knowledge(L.STALE_DAYS + 5, "VAT"))
        msgs = self.messages()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0][0], "WARN")
        self.assertIn(f"knowledge/tax/vat.md was last verified {L.STALE_DAYS + 5} days ago", msgs[0][1])
        self.assertIn("1 knowledge file(s) due for a re-check, e.g. knowledge/tax/vat.md", L.status(self.ws))

    def test_bad_missing_and_future_dates(self):
        write(self.ws / "knowledge/a.md", "---\nlast_verified: soon\n---\n\n# A\n")
        write(self.ws / "knowledge/b.md", "# B without a date\n")
        write(self.ws / "knowledge/c.md", knowledge(-3))
        text = L.format_doctor(L.doctor(self.ws))
        self.assertIn("WARN: knowledge/a.md: last_verified 'soon' is not a date", text)
        self.assertIn("INFO: knowledge/b.md has no last_verified date", text)
        self.assertIn("WARN: knowledge/c.md: in the future", text)

    def test_template_readme_and_inbox_are_not_checked(self):
        self.assertFalse([m for _, m in self.messages() if "_template.md" in m or "README.md" in m])

    def test_inbox_items_show_in_status(self):
        with open(self.ws / "knowledge/inbox.md", "a", encoding="utf-8", newline="\n") as f:
            f.write("\n---knowledge---\nDate: 2026-10-24\nTopic: VAT\nWhat: x\nSource: y\n---end---\n")
        self.assertIn("1 knowledge suggestion(s) in knowledge/inbox.md", L.status(self.ws))

    def test_without_the_module_only_stale_dates_warn(self):
        L.remove_module(self.ws, "knowledge-inbox", apply=True)
        write(self.ws / "knowledge/b.md", "# B without a date\n")
        self.assertEqual(self.messages(), [])
        write(self.ws / "knowledge/old.md", knowledge(400))
        self.assertEqual([lvl for lvl, _ in self.messages()], ["WARN"])

    def test_remove_keeps_the_humans_knowledge(self):
        write(self.ws / "knowledge/invoicing.md", knowledge(1))
        L.remove_module(self.ws, "knowledge-inbox", apply=True)
        self.assertTrue((self.ws / "knowledge/invoicing.md").is_file())
        self.assertFalse((self.ws / "knowledge/inbox.md").exists())
        self.assertTrue((self.ws / "knowledge").is_dir(), "the knowledge folder existed before the module")


if __name__ == "__main__":
    unittest.main()

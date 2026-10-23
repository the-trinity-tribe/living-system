"""Writing proposals with the tool, and the guided first decision it supports."""
import subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L

R = L.review_tool()
DATE = "2026-10-24"


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = L.init(Path(self.tmp.name) / "ws", "professional", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def propose(self, kind="new", title="Only I send things to clients",
                rule="Nothing goes to a client or gets published without my OK.", evidence="setup answer", **kw):
        return L.propose(self.ws, kind, title, rule, evidence, date=DATE, **kw)

    def approve(self, rel):
        return R.review(self.ws, rel, "approve", "Owner", date=DATE)

    def refused(self, **kw):
        before = snapshot(self.ws)
        with self.assertRaises(L.Refusal):
            self.propose(apply=True, **kw)
        self.assertEqual(snapshot(self.ws), before)


class TestFirstDecision(Case):
    def test_plan_writes_nothing_then_apply_review_and_current(self):
        before = snapshot(self.ws)
        rel, text = self.propose()
        self.assertEqual(rel, f"proposals/{DATE}-only-i-send-things-to-clients.md")
        self.assertEqual(snapshot(self.ws), before)
        self.propose(apply=True)
        self.assertEqual(R.check(self.ws), [])
        status, decision = self.approve(rel)
        self.assertEqual(status, "promoted")
        self.assertIn("## Rule\n\nNothing goes to a client or gets published without my OK.\n",
                      (self.ws / decision).read_text(encoding="utf-8"))
        self.assertEqual(R.current_decisions(self.ws), [decision])
        self.assertIn("Rules in force: 1 current decision(s)", L.status(self.ws))

    def test_titles_in_other_languages_make_plain_file_names(self):
        self.assertEqual(L.slugify("Nur ich schicke Angebote an Kunden"), "nur-ich-schicke-angebote-an-kunden")
        self.assertEqual(L.slugify("Tylko ja wysyłam oferty"), "tylko-ja-wysylam-oferty")
        self.assertEqual(L.slugify("Größe & Maß"), "grosse-mass")
        with self.assertRaises(L.Refusal):
            L.slugify("!!!")

    def test_multi_line_rule_becomes_one_quote(self):
        rel, _ = self.propose(rule="Nothing goes to a client without my OK.\n\nThis includes quotes and invoices.", apply=True)
        _, decision = self.approve(rel)
        self.assertIn("without my OK.\n\nThis includes quotes and invoices.", (self.ws / decision).read_text(encoding="utf-8"))

    def test_refusals_write_nothing(self):
        self.refused(rule="# A heading is not a rule")
        self.refused(rule="```\ncode\n```")
        self.refused(title="Two\nlines")
        self.refused(evidence="")
        self.refused(target="decisions/x.md")  # kind new has no target
        self.refused(kind="replace")  # needs a target
        self.refused(kind="nonsense")
        self.refused(why="## Heading")
        self.propose(apply=True)
        self.refused()  # the same file already exists


class TestChangingADecision(Case):
    def setUp(self):
        super().setUp()
        rel, _ = self.propose(apply=True)
        _, self.first = self.approve(rel)

    def test_exception_replace_and_retire_get_the_current_text_and_hash(self):
        for kind in ("exception", "replace", "retire"):
            with self.subTest(kind=kind):
                rel, text = self.propose(kind, title=f"{kind} test", rule="Alex may send routine updates.",
                                         evidence="team call", target=self.first)
                self.assertIn(f"target_sha256: {R.sha256(self.ws / self.first)}", text)
                self.assertIn("## Current canonical state\n\n> Nothing goes to a client", text)
                self.assertIn("Any attribution in it is not verified.", text)

    def test_replace_then_retire_through_review(self):
        rel, _ = self.propose("replace", title="Alex sends routine updates", rule="Alex may send routine updates; "
                              "everything else needs my OK.", evidence="team call", target=self.first, apply=True)
        _, second = self.approve(rel)
        self.assertEqual(R.current_decisions(self.ws), [second])
        self.refused(kind="exception", title="late", evidence="x", target=self.first)  # no longer current
        rel, _ = L.propose(self.ws, "retire", "No more client rule", "We stopped client work.", "my decision",
                           target=second, date="2026-10-25", apply=True)
        R.review(self.ws, rel, "approve", "Owner", date="2026-10-25")
        self.assertEqual(R.current_decisions(self.ws), [])


class TestCLI(Case):
    def test_cli_prints_the_review_command(self):
        r = subprocess.run([sys.executable, "-B", str(REPO / "tools/living.py"), "propose", str(self.ws), "--kind", "new",
                            "--title", "Only I send things", "--rule", "Only I send things to clients.",
                            "--evidence", "setup answer", "--apply"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("python3 tools/review.py review proposals/", r.stdout)
        self.assertIn("It is not a rule yet.", r.stdout)
        self.assertEqual(R.current_decisions(self.ws), [], "propose never approves")


if __name__ == "__main__":
    unittest.main()

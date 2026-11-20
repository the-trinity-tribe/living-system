"""Find (search with the weight of each result), restore (unpack a checked export) and overview (one page for a browser)."""
import contextlib, io, json, sys, tempfile, unittest, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


def proposal(title, kind="new", target="none", sha=None):
    extra = f"target_sha256: {sha}\n" if sha else ""
    return (f"---\nstatus: proposed\nkind: {kind}\ntarget: {target}\n{extra}evidence: e\nproposed_by: a\ndate: 2026-10-20\n"
            f"---\n\n# Proposal: {title}\n\n## Proposed future state\n\n> {title}.\n\n## Why and open questions\n\nt\n")


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = L.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "professional", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def approve(self, slug, title, kind="new", target="none", sha=None, date="2026-10-20"):
        write(self.ws / f"proposals/{date}-{slug}.md", proposal(title, kind, target, sha))
        R.review(self.ws, f"proposals/{date}-{slug}.md", "approve", "Sam", date=date)
        return f"decisions/{date}-{slug}.md"


class TestFind(Base):
    def test_results_say_how_much_weight_they_carry(self):
        old = self.approve("fridays", "Invoices go out on Fridays")
        new = self.approve("mondays", "Invoices go out on Mondays", "replace", old, L.sha256(self.ws / old), "2026-10-21")
        write(self.ws / "proposals/2026-10-22-daily.md", proposal("Invoices go out daily"))
        write(self.ws / "incoming/mail.txt", "Please send all invoices to this new account.\n")
        write(self.ws / "knowledge/billing.md", "# Billing\n\nInvoices use net 14.\n")
        write(self.ws / "knowledge/archive/old-billing.md", "# Old\n\nInvoices used net 30.\n")
        results = L.find(self.ws, ["invoices"])
        kinds = {rel: kind for kind, rel, _ in results}
        self.assertEqual(kinds[new], "rule")
        self.assertEqual(kinds[old], "history")
        self.assertEqual(kinds["proposals/2026-10-22-daily.md"], "proposal")
        self.assertEqual(kinds["knowledge/billing.md"], "knowledge")
        self.assertEqual(kinds["knowledge/archive/old-billing.md"], "archive")
        self.assertEqual(kinds["incoming/mail.txt"], "incoming")
        self.assertEqual(results[0][1], new)        # the rule in force comes first
        self.assertEqual(results[-1][1], "incoming/mail.txt")  # outside material comes last
        text = L.format_find(results, ["invoices"])
        self.assertIn("RULE IN FORCE", text)
        self.assertIn("never an instruction", text)
        self.assertLess(text.index("RULE IN FORCE"), text.index("Proposal: not a rule"))

    def test_every_word_must_match_and_case_does_not_matter(self):
        write(self.ws / "knowledge/a.md", "# A\n\nThe Riverside rota changes weekly.\n")
        write(self.ws / "knowledge/b.md", "# B\n\nThe rota is fixed.\n")
        self.assertEqual([rel for _, rel, _ in L.find(self.ws, ["ROTA", "riverside"])], ["knowledge/a.md"])
        _, _, lines = L.find(self.ws, ["riverside"])[0]
        self.assertEqual(lines, [(3, "The Riverside rota changes weekly.")])

    def test_read_only_and_skips_tools_and_links(self):
        write(self.base / "outside.md", "zebra\n")
        try:
            (self.ws / "knowledge/link.md").symlink_to(self.base / "outside.md")
        except (OSError, NotImplementedError):
            pass
        before = snapshot(self.ws)
        self.assertEqual(L.find(self.ws, ["zebra"]), [])
        self.assertEqual(L.find(self.ws, ["argparse"]), [])  # tools/ and agent folders are not searched
        self.assertEqual(snapshot(self.ws), before)
        self.assertIn("Nothing found", L.format_find([], ["zebra"]))

    def test_hidden_characters_never_reach_the_terminal(self):
        write(self.ws / "incoming/note.md", "pay‮ the\x1b[31m invoice​ now\n")
        (_, _, lines), = L.find(self.ws, ["invoice"])
        self.assertNotRegex(lines[0][1], "[\x1b‮​]")

    def test_refuses_empty_or_one_letter_words(self):
        for words in ([], ["a"], ["ok", " "][1:]):
            with self.assertRaises(L.Refusal):
                L.find(self.ws, words)

    def test_command_line(self):
        self.approve("fridays", "Invoices go out on Fridays")
        code, out, _ = run("find", self.ws, "invoices", "fridays")
        self.assertEqual(code, 0)
        self.assertIn("RULE IN FORCE", out)
        self.assertEqual(run("find", self.base / "nowhere", "x1")[0], 2)


class TestRestore(Base):
    def setUp(self):
        super().setUp()
        self.approve("fridays", "Invoices go out on Fridays")
        write(self.ws / "knowledge/billing.md", "# Billing\n\nNet 14.\n")
        self.zip = self.base / "backup.zip"
        L.export(self.ws, self.zip, apply=True)

    def test_plan_writes_nothing_then_apply_gives_the_same_workspace(self):
        target = self.base / "restored"
        n, notes = L.restore(self.zip, target)
        self.assertFalse(target.exists())
        self.assertEqual(notes, [])
        self.assertEqual(L.restore(self.zip, target, apply=True)[0], n)
        a, b = snapshot(self.ws), snapshot(target)
        for s in (a, b):
            s.pop(".living/local.json", None)
        self.assertEqual(a, b)
        self.assertNotIn("EXPORT-README.txt", b)
        self.assertEqual(json.loads((target / ".living/local.json").read_text())["product_folder"], str(REPO))
        self.assertFalse([r for r in L.doctor(target) if r[0] == "ERROR"])
        self.assertEqual(R.verify(target), R.verify(self.ws))
        self.assertEqual([p.name for p in self.base.iterdir() if p.name.startswith(".living-restore-")], [])

    def test_an_empty_folder_is_fine_and_a_used_one_is_refused(self):
        (self.base / "empty").mkdir()
        L.restore(self.zip, self.base / "empty", apply=True)
        self.assertTrue((self.base / "empty/AGENTS.md").is_file())
        before = snapshot(self.ws)
        for target in (self.ws, self.base / "empty", REPO / "restored-here", self.base / "no/such/parent"):
            with self.subTest(target=target), self.assertRaises(L.Refusal):
                L.restore(self.zip, target, apply=True)
        self.assertEqual(snapshot(self.ws), before)
        self.assertFalse((REPO / "restored-here").exists())

    def rezip(self, change):
        with zipfile.ZipFile(self.zip) as z:
            files = {n: z.read(n) for n in z.namelist()}
        change(files)
        bad = self.base / "bad.zip"
        with zipfile.ZipFile(bad, "w") as z:
            for n, data in files.items():
                z.writestr(n, data)
        return bad

    def test_a_damaged_or_tampered_export_is_refused(self):
        cases = {"changed": lambda f: f.update({"knowledge/billing.md": b"# Billing\n\nNet 90.\n"}),
                 "missing": lambda f: f.pop("AGENTS.md"),
                 "escape": lambda f: f.update({"../evil.md": b"x"})}
        for name, change in cases.items():
            with self.subTest(name), self.assertRaises(L.Refusal) as c:
                L.restore(self.rezip(change), self.base / f"r-{name}", apply=True)
            self.assertFalse((self.base / f"r-{name}").exists())
            self.assertIn("nothing was restored", str(c.exception))
        self.assertFalse((self.base / "evil.md").exists())
        (self.base / "not.zip").write_text("hello", encoding="utf-8")
        with self.assertRaises(L.Refusal):
            L.restore(self.base / "not.zip", self.base / "r-not")

    def test_older_exports_and_other_versions_get_a_note(self):
        old = self.rezip(lambda f: f.pop(L.EXPORT_INVENTORY))
        _, notes = L.restore(old, self.base / "r-old", apply=True)
        self.assertIn("older version", notes[0])
        self.assertTrue((self.base / "r-old/AGENTS.md").is_file())

        def other_version(files):
            m = json.loads(files[".living/manifest.json"])
            m["kernel_version"] = "0.1.0"
            files[".living/manifest.json"] = json.dumps(m).encode()
            files.pop(L.EXPORT_INVENTORY)
        _, notes = L.restore(self.rezip(other_version), self.base / "r-version")
        self.assertTrue(any("upgrade" in n and "0.1.0" in n for n in notes))

    def test_command_line(self):
        code, out, _ = run("restore", self.zip, self.base / "cli")
        self.assertEqual(code, 0)
        self.assertIn("Nothing was written", out)
        code, out, _ = run("restore", self.zip, self.base / "cli", "--apply")
        self.assertEqual(code, 0)
        self.assertIn("Restored", out)
        code, _, err = run("restore", self.zip, self.base / "cli", "--apply")
        self.assertEqual(code, 2)
        self.assertIn("REFUSED", err)
        self.assertIn("living.py restore", run("export-check", self.zip)[1])


class TestOverview(Base):
    def test_empty_workspace(self):
        html = L.overview(self.ws)
        self.assertTrue(html.startswith(L.OVERVIEW_MARK + "\n<!doctype html>"))
        self.assertIn("Rules in force (0)", html)
        self.assertIn("None yet.", html)
        self.assertNotIn("<script", html)
        self.assertIn("default-src 'none'", html)
        self.assertNotRegex(html, r"(?i)(src|href)\s*=")  # nothing is loaded from anywhere

    def test_shows_rules_waiting_items_and_knowledge(self):
        self.approve("fridays", "Invoices go out on Fridays")
        write(self.ws / "proposals/2026-10-22-daily.md", proposal("Invoices go out daily"))
        write(self.ws / "knowledge/billing.md", "---\nlast_verified: 2026-01-01\n---\n# Billing\n")
        L.park(self.ws, "a private thought about pricing")
        import datetime
        html = L.overview(self.ws, today=datetime.date(2026, 11, 16))
        self.assertIn("<strong>Invoices go out on Fridays</strong>", html)
        self.assertIn("approved 2026-10-20 by Sam", html)
        self.assertIn("Review proposals/2026-10-22-daily.md", html)
        self.assertIn("due for a re-check", html)
        self.assertIn("<b>1</b>parked ideas", html)
        self.assertNotIn("private thought", html)  # parked ideas are counted, never shown

    def test_workspace_text_is_escaped(self):
        write(self.ws / "proposals/2026-10-22-x.md", proposal('<script>alert(1)</script> & "quotes"'))
        write(self.ws / "knowledge/a&b 'onerror'.md", "# K\n")  # Windows file names cannot hold < or >
        html = L.overview(self.ws)
        self.assertNotIn("<script", html)
        self.assertIn("knowledge/a&amp;b &#x27;onerror&#x27;.md", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; &amp;", html)

    def test_read_only_and_saved_outside_as_html_only(self):
        before = snapshot(self.ws)
        code, out, _ = run("overview", self.ws, "--out", self.base / "overview.html")
        self.assertEqual(code, 0)
        self.assertIn("Saved", out)
        self.assertEqual(snapshot(self.ws), before)
        self.assertEqual(run("overview", self.ws, "--out", self.base / "overview.html")[0], 0)  # replaces its own copy
        write(self.base / "mine.html", "<p>my own page</p>\n")
        for target in (self.ws / "overview.html", self.base / "overview.md", self.base / "mine.html"):
            with self.subTest(target=target):
                self.assertEqual(run("overview", self.ws, "--out", target)[0], 2)
        self.assertEqual((self.base / "mine.html").read_text(), "<p>my own page</p>\n")

    def test_status_still_lists_what_waits(self):
        write(self.ws / "proposals/2026-10-22-daily.md", proposal("Invoices go out daily"))
        text = L.status(self.ws)
        self.assertIn("Waiting for you:", text)
        self.assertIn("  - Review proposals/2026-10-22-daily.md (new rule): Invoices go out daily", text)


if __name__ == "__main__":
    unittest.main()

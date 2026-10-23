"""Replacing and retiring decisions (`kind: replace`, `kind: retire`)."""
import sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import review as R

OLD = "decisions/2026-10-01-weekly-update-owner.md"
OLD_TEXT = """---
status: approved
approved_by: Owner
date: 2026-10-01
source_proposal: proposals/2026-09-30-weekly-update-owner.md
---

# Alex owns the weekly client update

## Rule

Alex prepares and sends the weekly client update every Friday.

## Why

See source proposal.

## Scope

As stated in the Rule.

## Provenance

Created from `proposals/2026-09-30-weekly-update-owner.md`. `approved_by` is attribution, not verified identity.
"""


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


def proposal(kind, target, digest, title="Sam owns the weekly client update",
             quote="> Sam prepares the weekly client update every Friday. Alex reviews it."):
    sha = f"target_sha256: {digest}\n" if digest is not None else ""
    return (f"---\nstatus: proposed\nkind: {kind}\ntarget: {target}\n{sha}evidence: team call 2026-10-20\n"
            f"proposed_by: agent\ndate: 2026-10-20\n---\n\n# Proposal: {title}\n\nNot current truth.\n\n"
            f"## Proposed future state\n\n{quote}\n\n## Why and open questions\n\nRaised in the call.\n")


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for f in ("AGENTS.md", "CONTEXT-ROUTING.md", "SYSTEM.md", "PRINCIPLES.md", "README.md"):
            (self.root / f).write_text(f"# {f}\n", encoding="utf-8", newline="\n")
        (self.root / "decisions").mkdir()
        (self.root / "proposals").mkdir()
        (self.root / OLD).write_text(OLD_TEXT, encoding="utf-8", newline="\n")
        self.digest = R.sha256(self.root / OLD)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, text):
        (self.root / f"proposals/{name}").write_text(text, encoding="utf-8", newline="\n")
        self.before = snapshot(self.root)
        return f"proposals/{name}"

    def review(self, rel, outcome="approve"):
        return R.review(self.root, rel, outcome, "Owner", date="2026-10-21")

    def refused(self, rel, outcome="approve"):
        with self.assertRaises(R.Refusal):
            self.review(rel, outcome)
        self.assertEqual(snapshot(self.root), self.before)


class TestReplace(Case):
    def test_replace_supersedes_and_keeps_history(self):
        rel = self.put("2026-10-20-sam-owns-update.md", proposal("replace", OLD, self.digest))
        self.assertEqual(R.check(self.root), [])
        status, new = self.review(rel)
        self.assertEqual((status, new), ("promoted", "decisions/2026-10-21-sam-owns-update.md"))
        text = (self.root / new).read_text()
        self.assertIn(f"supersedes: {OLD}\n", text)
        self.assertIn("# Sam owns the weekly client update\n", text)
        self.assertIn("## Rule\n\nSam prepares the weekly client update every Friday. Alex reviews it.\n", text)
        self.assertNotIn("Alex prepares and sends", text, "a replacement does not carry the old rule")
        self.assertEqual((self.root / OLD).read_text(), OLD_TEXT, "the old decision is never edited")
        self.assertEqual(R.current_decisions(self.root), [new])
        self.assertEqual(R.check(self.root), [])

    def test_replaced_decision_can_itself_be_amended(self):
        rel = self.put("2026-10-20-sam-owns-update.md", proposal("replace", OLD, self.digest))
        _, new = self.review(rel)
        rel2 = self.put("2026-10-22-holiday-cover.md", proposal("exception", new, R.sha256(self.root / new),
                        quote="> In August, Alex covers it."))
        _, newer = R.review(self.root, rel2, "approve", "Owner", date="2026-10-23")
        self.assertEqual(R.current_decisions(self.root), [newer])

    def test_replace_refusals(self):
        cases = {"stale.md": proposal("replace", OLD, "0" * 64), "nohash.md": proposal("replace", OLD, None),
                 "none.md": proposal("replace", "none", self.digest),
                 "missing.md": proposal("replace", "decisions/2026-01-01-nope.md", self.digest),
                 "notitle.md": proposal("replace", OLD, self.digest).replace("# Proposal: ", "# ")}
        for name, text in cases.items():
            with self.subTest(case=name):
                self.refused(self.put(f"2026-10-20-{name}", text))

    def test_reject_and_defer_change_no_decision(self):
        for outcome in ("reject", "defer"):
            with self.subTest(outcome=outcome):
                rel = self.put(f"2026-10-20-{outcome}.md", proposal("replace", OLD, self.digest))
                self.review(rel, outcome)
                self.assertEqual(R.current_decisions(self.root), [OLD])


class TestRetire(Case):
    def retire(self):
        rel = self.put("2026-10-20-no-weekly-update.md",
                       proposal("retire", OLD, self.digest, title="Stop the weekly client update",
                                quote="> The client now gets a monthly report instead."))
        return self.review(rel)[1]

    def test_retire_leaves_no_current_rule_and_keeps_history(self):
        record = self.retire()
        text = (self.root / record).read_text()
        self.assertIn("kind: retirement\n", text)
        self.assertIn(f"supersedes: {OLD}\n", text)
        self.assertIn("# Retired: Alex owns the weekly client update\n", text)
        self.assertIn("This record is not a rule.", text)
        self.assertIn("## Why\n\nThe client now gets a monthly report instead.\n", text)
        self.assertNotIn("## Rule", text)
        self.assertEqual(R.current_decisions(self.root), [])
        self.assertEqual((self.root / OLD).read_text(), OLD_TEXT)
        self.assertEqual(R.check(self.root), [])

    def test_retirement_record_cannot_be_amended_replaced_or_retired(self):
        record = self.retire()
        digest = R.sha256(self.root / record)
        for kind in ("exception", "replace", "retire"):
            with self.subTest(kind=kind):
                self.refused(self.put(f"2026-10-22-{kind}.md", proposal(kind, record, digest)))

    def test_retired_rule_can_come_back_as_new(self):
        self.retire()
        rel = self.put("2026-10-22-weekly-again.md", proposal("new", "none", None, title="Weekly update again",
                       quote="> Alex sends the weekly client update again."))
        _, new = R.review(self.root, rel, "approve", "Owner", date="2026-10-23")
        self.assertEqual(R.current_decisions(self.root), [new])

    def test_retiring_an_already_superseded_decision_is_refused(self):
        self.retire()
        self.refused(self.put("2026-10-22-again.md", proposal("retire", OLD, self.digest)))

    def test_check_flags_broken_retirement_records(self):
        (self.root / "decisions/2026-10-25-bad.md").write_text("---\nstatus: approved\nkind: retirement\n---\n\n# x\n", encoding="utf-8", newline="\n")
        (self.root / "decisions/2026-10-26-odd.md").write_text("---\nstatus: approved\nkind: memo\n---\n\n# x\n", encoding="utf-8", newline="\n")
        problems = "\n".join(R.check(self.root))
        self.assertIn("must name the decision it retires", problems)
        self.assertIn("unexpected kind memo", problems)


if __name__ == "__main__":
    unittest.main()

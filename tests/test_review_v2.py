"""Proposals that create a new decision (`kind: new`), and all-or-nothing writes.

Uses a self-contained empty workspace, so it does not depend on the demo files.
"""
import os, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import review as R

PROPOSAL = "proposals/2026-10-20-weekly-update-owner.md"
NEW = "decisions/2026-10-21-weekly-update-owner.md"

FRONT = """---
status: proposed
kind: new
target: none
evidence: team meeting notes, 2026-10-20
proposed_by: agent
date: 2026-10-20
---
"""

BODY = """
# Proposal: Alex owns the weekly client update

Not current truth.

## Proposed future state

> Alex prepares and sends the weekly client update every Friday.

## Why and open questions

Raised in the team meeting. Open: who covers holidays?
"""

EXPECTED = """---
status: approved
approved_by: Test Reviewer
date: 2026-10-21
source_proposal: proposals/2026-10-20-weekly-update-owner.md
---

# Alex owns the weekly client update

## Rule

Alex prepares and sends the weekly client update every Friday.

## Why

See source proposal.

## Scope

As stated in the Rule.

## Provenance

Created from `proposals/2026-10-20-weekly-update-owner.md`. `approved_by` is attribution, not verified identity.
"""


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


class EmptyWorkspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for f in ("AGENTS.md", "CONTEXT-ROUTING.md", "SYSTEM.md", "PRINCIPLES.md", "README.md"):
            (self.root / f).write_text(f"# {f}\n")
        (self.root / "decisions").mkdir()
        (self.root / "proposals").mkdir()
        self.write_proposal(FRONT + BODY)

    def tearDown(self):
        self.tmp.cleanup()

    def write_proposal(self, text, rel=PROPOSAL):
        (self.root / rel).write_text(text)
        self.before = snapshot(self.root)

    def run_review(self, outcome, rel=PROPOSAL):
        return R.review(self.root, rel, outcome, "Test Reviewer", date="2026-10-21")

    def assertRefused(self, outcome="approve", rel=PROPOSAL):
        with self.assertRaises(R.Refusal):
            self.run_review(outcome, rel)
        self.assertEqual(snapshot(self.root), self.before, "a refusal must write nothing")


class TestNewDecision(EmptyWorkspace):
    def test_check_accepts_new_proposal(self):
        self.assertEqual(R.check(self.root), [])

    def test_approve_creates_exact_decision(self):
        status, result = self.run_review("approve")
        self.assertEqual((status, result), ("promoted", NEW))
        self.assertEqual((self.root / NEW).read_text(), EXPECTED)
        self.assertEqual(R.current_decisions(self.root), [NEW])
        meta, _, body = R.split_frontmatter((self.root / PROPOSAL).read_text(), PROPOSAL)
        self.assertEqual(meta["status"], "promoted")
        self.assertEqual(meta["resulting_decision"], NEW)
        self.assertIn("| approve | by Test Reviewer (attribution, not verified)", body)
        self.assertEqual(R.check(self.root), [])

    def test_approve_is_deterministic(self):
        self.run_review("approve")
        first = snapshot(self.root)
        other = EmptyWorkspace("run")
        other.setUp()
        try:
            other.run_review("approve")
            self.assertEqual(snapshot(other.root), first)
        finally:
            other.tearDown()

    def test_reject_and_defer_leave_decisions_empty(self):
        for outcome, status in (("reject", "rejected"), ("defer", "deferred")):
            with self.subTest(outcome=outcome):
                self.write_proposal(FRONT + BODY)
                self.assertEqual(self.run_review(outcome), (status, ""))
                self.assertEqual(list((self.root / "decisions").iterdir()), [])

    def test_defer_then_approve(self):
        self.run_review("defer")
        self.assertEqual(self.run_review("approve"), ("promoted", NEW))

    def test_promoted_is_terminal(self):
        self.run_review("approve")
        self.before = snapshot(self.root)
        self.assertRefused()

    def test_existing_result_file_blocks(self):
        (self.root / NEW).write_text("---\nstatus: approved\n---\n# taken\n")
        self.before = snapshot(self.root)
        self.assertRefused()

    def test_creates_missing_decisions_folder(self):
        (self.root / "decisions").rmdir()
        self.assertEqual(self.run_review("approve"), ("promoted", NEW))
        self.assertTrue((self.root / NEW).is_file())


class TestNewDecisionRefusals(EmptyWorkspace):
    def test_missing_title(self):
        self.write_proposal(FRONT + BODY.replace("# Proposal: ", "# "))
        self.assertRefused()

    def test_two_blockquotes(self):
        self.write_proposal(FRONT + BODY.replace("every Friday.", "every Friday.\n\nmore\n\n> second"))
        self.assertRefused()

    def test_kind_new_needs_target_none(self):
        self.write_proposal(FRONT.replace("target: none", "target: decisions/x.md") + BODY)
        self.assertRefused()
        self.assertRefused("reject")

    def test_kind_new_rejects_hash(self):
        self.write_proposal(FRONT.replace("target: none", "target: none\ntarget_sha256: abc") + BODY)
        self.assertRefused()

    def test_target_none_needs_kind_new(self):
        self.write_proposal(FRONT.replace("kind: new\n", "") + BODY)
        self.assertRefused()
        self.assertIn("target: none requires kind: new", "\n".join(R.check(self.root)))

    def test_unknown_kind(self):
        self.write_proposal(FRONT.replace("kind: new", "kind: replace") + BODY)
        self.assertRefused()
        self.assertIn("unknown kind", "\n".join(R.check(self.root)))


class TestAllOrNothingWrites(EmptyWorkspace):
    def test_failed_second_write_leaves_workspace_unchanged(self):
        real = os.replace
        calls = []

        def fail_second(src, dst):
            calls.append(dst)
            if len(calls) == 2:
                raise OSError("disk full (simulated)")
            return real(src, dst)

        with mock.patch.object(R.os, "replace", fail_second):
            with self.assertRaises(OSError):
                self.run_review("approve")
        self.assertEqual(snapshot(self.root), self.before)

    def test_failed_temp_write_leaves_workspace_unchanged(self):
        with mock.patch.object(Path, "write_text", side_effect=OSError("read-only (simulated)")):
            with self.assertRaises(OSError):
                self.run_review("approve")
        self.assertEqual(snapshot(self.root), self.before)


if __name__ == "__main__":
    unittest.main()

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


def can_link():
    """Windows may refuse to create links without extra rights; those tests are skipped there."""
    with tempfile.TemporaryDirectory() as d:
        try:
            os.symlink(d, os.path.join(d, "link"))
            return True
        except (OSError, NotImplementedError):
            return False


CAN_LINK = can_link()


def snapshot(root):
    """Every file's bytes, and every folder (so leftover folders count as changes)."""
    return {p.relative_to(root).as_posix() + ("/" if p.is_dir() else ""): p.read_bytes() if p.is_file() else b""
            for p in sorted(Path(root).rglob("*"))}


class EmptyWorkspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for f in ("AGENTS.md", "CONTEXT-ROUTING.md", "SYSTEM.md", "PRINCIPLES.md", "README.md"):
            (self.root / f).write_text(f"# {f}\n", encoding="utf-8", newline="\n")
        (self.root / "decisions").mkdir()
        (self.root / "proposals").mkdir()
        self.write_proposal(FRONT + BODY)

    def tearDown(self):
        self.tmp.cleanup()

    def write_proposal(self, text, rel=PROPOSAL):
        (self.root / rel).write_text(text, encoding="utf-8", newline="\n")
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
        self.assertEqual((self.root / NEW).read_text(encoding="utf-8"), EXPECTED)
        self.assertEqual(R.current_decisions(self.root), [NEW])
        meta, _, body = R.split_frontmatter((self.root / PROPOSAL).read_text(encoding="utf-8"), PROPOSAL)
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
        (self.root / NEW).write_text("---\nstatus: approved\n---\n# taken\n", encoding="utf-8", newline="\n")
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
        self.write_proposal(FRONT.replace("kind: new", "kind: rewrite") + BODY)
        self.assertRefused()
        self.assertIn("unknown kind", "\n".join(R.check(self.root)))


class TestAllOrNothingWrites(EmptyWorkspace):
    def test_failed_proposal_update_removes_new_decision(self):
        with mock.patch.object(R.os, "replace", side_effect=OSError("disk full (simulated)")):
            with self.assertRaises(OSError):
                self.run_review("approve")
        self.assertEqual(snapshot(self.root), self.before)

    def test_failed_write_midway_leaves_nothing_behind(self):
        (self.root / "decisions").rmdir()
        self.before = snapshot(self.root)
        real_open = open

        class Broken:
            def __init__(self, f): self.f = f
            def __enter__(self): return self
            def __exit__(self, *a): self.f.close()
            def write(self, text):
                self.f.write(text[:10])
                raise OSError("disk full (simulated)")

        with mock.patch.object(R, "open", create=True, side_effect=lambda *a, **k: Broken(real_open(*a, **k))):
            with self.assertRaises(OSError):
                self.run_review("approve")
        self.assertEqual(snapshot(self.root), self.before, "no half-written decision and no new folder")

    @unittest.skipIf(os.name == "nt", "Windows has no Unix permission bits")
    def test_proposal_keeps_its_file_permissions(self):
        os.chmod(self.root / PROPOSAL, 0o640)
        self.run_review("defer")
        self.assertEqual(os.stat(self.root / PROPOSAL).st_mode & 0o777, 0o640)


class TestHardening(EmptyWorkspace):
    """Regression tests for review findings: each input must be refused and write nothing."""

    def test_line_breaks_in_reviewer_or_note_are_refused(self):
        for by, note in (("Alex\rsupersedes: decisions/x.md", ""), ("Alex\n", ""), ("Alex", "a\u2028b"),
                         ("Al\x00ex", "")):
            with self.subTest(by=by, note=note):
                with self.assertRaises(R.Refusal):
                    R.review(self.root, PROPOSAL, "approve", by, note, date="2026-10-21")
                self.assertEqual(snapshot(self.root), self.before)

    def test_noncanonical_paths_are_refused(self):
        for rel in ("proposals/./2026-10-20-weekly-update-owner.md", "proposals//2026-10-20-weekly-update-owner.md",
                    "proposals\\2026-10-20-weekly-update-owner.md"):
            with self.subTest(rel=rel):
                with self.assertRaises(R.Refusal):
                    R.review(self.root, rel, "approve", "Test Reviewer", date="2026-10-21")
        self.assertEqual(snapshot(self.root), self.before)

    def test_lazy_continuation_line_is_refused(self):
        self.write_proposal(FRONT + BODY.replace("every Friday.", "every Friday,\nunless Sam does it."))
        self.assertRefused()

    def test_rule_inside_code_block_is_refused(self):
        self.write_proposal(FRONT + BODY.replace("> Alex prepares", "```\n> Alex prepares").replace(
            "every Friday.\n", "every Friday.\n```\n"))
        self.assertRefused()

    def test_heading_inside_rule_is_refused(self):
        self.write_proposal(FRONT + BODY.replace("every Friday.", "every Friday.\n>\n> ## Why\n> because"))
        self.assertRefused()

    @unittest.skipUnless(CAN_LINK, "this system cannot create links")
    def test_linked_proposal_is_refused(self):
        real = self.root / "real.md"
        real.write_text(FRONT + BODY, encoding="utf-8", newline="\n")
        (self.root / PROPOSAL).unlink()
        (self.root / PROPOSAL).symlink_to(real)
        self.before = snapshot(self.root)
        self.assertRefused()

    @unittest.skipUnless(CAN_LINK, "this system cannot create links")
    def test_link_in_place_of_new_decision_is_not_followed(self):
        target = self.root / "outside.md"
        target.write_text("keep me\n", encoding="utf-8", newline="\n")
        (self.root / NEW).symlink_to(target)
        self.before = snapshot(self.root)
        self.assertRefused()
        self.assertEqual(target.read_text(encoding="utf-8"), "keep me\n")

    def test_concurrent_review_is_refused_and_lock_is_released(self):
        (self.root / ".review.lock").write_text("", encoding="utf-8", newline="\n")
        self.before = snapshot(self.root)
        self.assertRefused()
        (self.root / ".review.lock").unlink()
        self.run_review("approve")
        self.assertFalse((self.root / ".review.lock").exists())

    def test_missing_workspace_is_refused_by_the_cli(self):
        import subprocess
        tool = Path(R.__file__)
        for cmd in ("current", "check"):
            r = subprocess.run([sys.executable, "-B", str(tool), "--root", str(self.root / "nope"), cmd],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 2, cmd)
        r = subprocess.run([sys.executable, "-B", str(tool), "--root", str(self.root), "current"],
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout), (0, "\n"))

    def test_non_ascii_text_round_trips(self):
        self.write_proposal(FRONT + BODY.replace("Alex prepares", "Łukasz przygotowuje"))
        R.review(self.root, PROPOSAL, "approve", "Zoë Müller", date="2026-10-21")
        self.assertIn("Łukasz przygotowuje", (self.root / NEW).read_text(encoding="utf-8"))
        self.assertIn("Zoë Müller", (self.root / NEW).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

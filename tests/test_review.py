import hashlib, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIX = Path(__file__).resolve().parent / "fixtures"  # frozen pre-promotion state
sys.path.insert(0, str(REPO / "tools"))
import review as R

PROPOSAL = "proposals/2026-09-28-leo-signs-off-riverside-rota-updates.md"
TARGET = "decisions/2026-09-01-founder-approves-client-deliverables.md"
NEW = "decisions/2026-10-08-leo-signs-off-riverside-rota-updates.md"


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for d in ("projects", "knowledge", "examples"):
            shutil.copytree(REPO / d, self.root / d)
        for d in ("decisions", "proposals"):
            shutil.copytree(FIX / d, self.root / d)
        for f in ("AGENTS.md", "CONTEXT-ROUTING.md", "SYSTEM.md", "PRINCIPLES.md", "README.md"):
            shutil.copy(REPO / f, self.root / f)
        self.before = snapshot(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def run_review(self, outcome, by="Test Reviewer", proposal=PROPOSAL, **kw):
        return R.review(self.root, proposal, outcome, by, date="2026-10-08", **kw)

    def changed(self):
        after = snapshot(self.root)
        return {k for k in set(after) | set(self.before) if after.get(k) != self.before.get(k)}


class TestSlice3(Fixture):
    def test_no_review_no_change(self):
        self.assertEqual(self.changed(), set())
        self.assertEqual(R.current_decisions(self.root), [TARGET])

    def test_approve_exact_result(self):
        status, result = self.run_review("approve")
        self.assertEqual((status, result), ("promoted", NEW))
        self.assertEqual(self.changed(), {NEW, PROPOSAL})  # nothing beyond target/result
        old = (FIX / TARGET).read_text()
        expected = f"""---
status: approved
approved_by: Test Reviewer
date: 2026-10-08
supersedes: {TARGET}
source_proposal: {PROPOSAL}
---

# Require Maya approval for client-facing deliverables (amended)

## Rule

All client-facing deliverables require Maya Chen's approval before they are sent.

### Exception

For the Riverside Community Garden project, Leo Martin may approve routine schedule updates sent to the garden, such as a revised volunteer rota, before they are sent. This exception does not cover anything involving unusual commitments, pricing changes, or anything that could affect Moss & Circuit's reputation; those still require Maya Chen's approval. All other client-facing deliverables still require Maya Chen's approval.

## Why

Moss & Circuit centralised external approval with the founder to keep quality and consistency while the studio's delivery process was still immature.

## Scope

Subject to the Exception under Rule.

Applies to every client-facing deliverable, for every client and project, regardless of who prepared it.

## Provenance

Promoted from `{PROPOSAL}` and supersedes `{TARGET}`. `approved_by` is attribution, not verified identity.
"""
        self.assertEqual((self.root / NEW).read_text(), expected)
        self.assertEqual((self.root / TARGET).read_text(), old)  # history untouched
        self.assertEqual(R.current_decisions(self.root), [NEW])
        p = (self.root / PROPOSAL).read_text()
        self.assertIn("status: promoted\n", p)
        self.assertIn(f"resulting_decision: {NEW}\n", p)
        self.assertIn("reviewed_by: Test Reviewer\n", p)
        self.assertTrue(p.rstrip().endswith(
            f"- 2026-10-08 | approve | by Test Reviewer (attribution, not verified) | resulting decision: {NEW}"))

    def test_approve_is_deterministic(self):
        self.run_review("approve")
        first = (self.root / NEW).read_bytes()
        (self.root / NEW).unlink()
        for k, v in self.before.items():
            (self.root / k).write_bytes(v)
        self.run_review("approve")
        self.assertEqual((self.root / NEW).read_bytes(), first)

    def _non_canonical(self, outcome, status):
        self.run_review(outcome, note="needs Maya confirmation")
        self.assertEqual(self.changed(), {PROPOSAL})
        p = (self.root / PROPOSAL).read_text()
        self.assertIn(f"status: {status}\n", p)
        self.assertIn(f"| {outcome} | by Test Reviewer", p)
        self.assertIn("note: needs Maya confirmation", p)
        self.assertNotIn("resulting_decision", p)
        self.assertEqual(R.current_decisions(self.root), [TARGET])
        self.assertEqual(R.check(self.root), [])

    def test_reject(self):
        self._non_canonical("reject", "rejected")

    def test_defer(self):
        self._non_canonical("defer", "deferred")

    def test_defer_then_approve(self):
        self.run_review("defer")
        self.run_review("approve")
        p = (self.root / PROPOSAL).read_text()
        self.assertEqual(p.count("reviewed_by:"), 1)
        self.assertEqual(p.count("\n- 2026-10-08 |"), 2)
        self.assertEqual(R.current_decisions(self.root), [NEW])

    def refuses(self, outcome="approve", **kw):
        before = snapshot(self.root)
        with self.assertRaises(R.Refusal):
            self.run_review(outcome, **kw)
        self.assertEqual(snapshot(self.root), before)  # fail closed: nothing written

    def test_stale_target(self):
        t = self.root / TARGET
        t.write_text(t.read_text() + "\nExtra line.\n")
        self.refuses()

    def test_second_promotion(self):
        self.run_review("approve")
        self.refuses()
        self.refuses("reject")

    def test_rejected_is_terminal(self):
        self.run_review("reject")
        self.refuses("approve")

    def test_second_proposal_on_superseded_target(self):
        self.run_review("approve")
        other = "proposals/2026-10-01-other.md"
        text = (FIX / PROPOSAL).read_text()
        (self.root / other).write_text(text)
        self.refuses(proposal=other)

    def test_malformed_future_state(self):
        p = self.root / PROPOSAL
        s = p.read_text()
        two = s.replace("## Why and open questions", "> second quote\n\n## Why and open questions")
        p.write_text(two)
        self.refuses()
        p.write_text(s.replace("> For the Riverside", "For the Riverside").replace("> This exception", "This exception"))
        self.refuses()
        p.write_text(s.replace("## Proposed future state", "## Proposed future states"))
        self.refuses()

    def test_missing_hash_and_bad_input(self):
        p = self.root / PROPOSAL
        s = p.read_text()
        p.write_text("\n".join(l for l in s.split("\n") if not l.startswith("target_sha256")))
        self.refuses()
        p.write_text(s)
        self.refuses(by="  ")
        self.refuses(note="a\nb")
        with self.assertRaises(R.Refusal):
            R.review(self.root, PROPOSAL, "maybe", "x", date="2026-10-08")
        self.refuses(proposal="proposals/../decisions/x.md")

    def test_existing_result_file_blocks(self):
        (self.root / NEW).write_text("x")
        self.refuses()


class TestRealRepoState(unittest.TestCase):
    """Real promotion, approved by Maya Chen (attribution) on 2026-10-07."""
    NEWREAL = "decisions/2026-10-07-leo-signs-off-riverside-rota-updates.md"

    def test_old_decision_byte_identical_history(self):
        self.assertEqual((REPO / TARGET).read_bytes(), (FIX / TARGET).read_bytes())

    def test_pinned_hash_matches_old_target(self):
        h = hashlib.sha256((REPO / TARGET).read_bytes()).hexdigest()
        self.assertIn(f"target_sha256: {h}\n", (REPO / PROPOSAL).read_text())

    def test_real_promotion_recorded(self):
        meta, _, body = R.split_frontmatter((REPO / PROPOSAL).read_text(), PROPOSAL)
        self.assertEqual(meta["status"], "promoted")
        self.assertEqual(meta["reviewed_by"], "Maya Chen")
        self.assertEqual(meta["resulting_decision"], self.NEWREAL)
        self.assertEqual(R.current_decisions(REPO), [self.NEWREAL])
        d, _, dbody = R.split_frontmatter((REPO / self.NEWREAL).read_text(), self.NEWREAL)
        self.assertEqual((d["status"], d["supersedes"], d["source_proposal"]), ("approved", TARGET, PROPOSAL))
        quote = R.single_blockquote(R.section(R.split_frontmatter((FIX / PROPOSAL).read_text(), "f")[2],
                                              "Proposed future state", "f"), "f")
        self.assertIn(f"### Exception\n\n{quote}\n", dbody)

    def test_promoted_proposal_cannot_be_reapplied(self):
        with self.assertRaises(R.Refusal):
            R.review(REPO, PROPOSAL, "approve", "x", date="2026-10-08")


class TestSlice1And2Regression(unittest.TestCase):
    def test_structure(self):
        self.assertEqual(R.check(REPO), [])

    def test_slice1_entry_and_authority(self):
        agents = (REPO / "AGENTS.md").read_text()
        self.assertIn("CONTEXT-ROUTING.md", agents)
        self.assertIn("Task authority is not canonical authority", agents)
        self.assertIn("Proposals are not on this list", agents)
        self.assertEqual((REPO / "CLAUDE.md").read_text().strip(), "@AGENTS.md")
        self.assertIn("status: approved", (REPO / "SYSTEM.md").read_text())

    def test_slice2_proposal_shape(self):
        text = (FIX / PROPOSAL).read_text()
        meta, _, body = R.split_frontmatter(text, PROPOSAL)
        self.assertEqual(meta["target"], TARGET)
        for h in ("Current canonical state", "New evidence", "Proposed future state", "Why and open questions"):
            R.section(body, h, PROPOSAL)
        quoted = R.section(body, "Current canonical state", PROPOSAL)
        rule = R.section(R.split_frontmatter((FIX / TARGET).read_text(), TARGET)[2], "Rule", TARGET)
        self.assertIn(rule, quoted)  # quoted exactly from target
        self.assertTrue(text.split("---\n", 2)[2].lstrip().startswith("# Proposal:"))
        self.assertIn("Not current truth.", text)

    def test_approved_decision_unchanged(self):
        # Slice 1 canonical decision must keep its approved content.
        t = (REPO / TARGET).read_text()
        self.assertIn("approved_by: Maya Chen", t)
        self.assertIn("All client-facing deliverables require Maya Chen's approval before they are sent.", t)


class TestSlice4(unittest.TestCase):
    CURRENT = TestRealRepoState.NEWREAL

    def test_project_routes_to_current_decision(self):
        text = (REPO / "projects/riverside-community-garden.md").read_text()
        applies = text.split("## Decisions that apply", 1)[1].split("\n## ", 1)[0]
        self.assertIn(self.CURRENT, applies)
        self.assertNotIn(TARGET, applies)

    def test_check_flags_project_reference_to_superseded_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("decisions", "proposals", "projects", "knowledge", "examples"):
                shutil.copytree(REPO / d, root / d)
            for f in ("AGENTS.md", "CONTEXT-ROUTING.md", "SYSTEM.md", "PRINCIPLES.md", "README.md"):
                shutil.copy(REPO / f, root / f)
            self.assertEqual(R.check(root), [])
            (root / "projects/other.md").write_text(f"# P\n\nSee `{TARGET}`.\n")
            self.assertEqual(R.check(root), [f"projects/other.md: references superseded decision {TARGET}"])

    def test_agents_promoted_proposal_rule(self):
        agents = (REPO / "AGENTS.md").read_text()
        self.assertIn("Promoted proposals are provenance only.", agents)
        self.assertIn("must not override, narrow or reopen", agents)


class TestCLI(Fixture):
    def cli(self, *args):
        return subprocess.run([sys.executable, str(REPO / "tools/review.py"), "--root", str(self.root), *args],
                              capture_output=True, text=True)

    def test_cli_defer_and_refusal_codes(self):
        r = self.cli("review", PROPOSAL, "--outcome", "defer", "--by", "T", "--date", "2026-10-08")
        self.assertEqual(r.returncode, 0)
        self.assertIn("canonical state unchanged", r.stdout)
        r = self.cli("review", PROPOSAL, "--outcome", "approve")  # missing --by
        self.assertEqual(r.returncode, 2)  # argparse error
        self.assertEqual(self.cli("current").stdout.strip(), TARGET)


if __name__ == "__main__":
    unittest.main()

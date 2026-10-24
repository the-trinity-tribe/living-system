"""Regression tests for the seventh code review (agency, delegation, agreement, compost, atlas)."""
import datetime, json, os, stat, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R

TODAY = datetime.date(2026, 10, 24)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "manager", "en")

    def tearDown(self):
        self.tmp.cleanup()

    def approve_all(self, ws=None):
        ws = ws or self.ws
        for p in sorted((ws / "proposals").glob("*.md")):
            if "status: proposed" in p.read_text(encoding="utf-8"):
                R.review(ws, f"proposals/{p.name}", "approve", "Ann")


class TestCompost(Case):
    def setUp(self):
        super().setUp()
        write(self.ws / "knowledge/note.md", "# Note\n\nv1\n")

    def test_a_save_just_before_the_lock_is_kept(self):  # finding 1
        real = L.workspace_lock

        def saving_lock(ws):
            write(self.ws / "knowledge/note.md", "# Note\n\nv2 saved just now\n")
            return real(ws)
        with mock.patch.object(L, "workspace_lock", saving_lock):
            L.compost(self.ws, "knowledge/note.md", "old", apply=True)
        self.assertIn("v2 saved just now", (self.ws / "knowledge/archive/note.md").read_text(encoding="utf-8"))

    @unittest.skipIf(os.name == "nt", "file modes differ on Windows")
    def test_archive_copy_is_no_more_readable(self):  # finding 2
        os.chmod(self.ws / "knowledge/note.md", 0o600)
        L.compost(self.ws, "knowledge/note.md", "old", apply=True)
        self.assertEqual(stat.S_IMODE(os.stat(self.ws / "knowledge/archive/note.md").st_mode), 0o600)

    def test_bom_front_matter_is_kept_as_one_block(self):  # finding 18
        (self.ws / "knowledge/bom.md").write_bytes("﻿---\nconfidence: low\n---\n\n# B\n".encode("utf-8"))
        _, text = L.compost(self.ws, "knowledge/bom.md", "old")
        self.assertTrue(text.startswith("---\narchived_on:"))
        self.assertEqual(text.count("---\n"), 2)
        self.assertIn("confidence: low", text)

    def test_archived_notes_leave_reference_upkeep(self):  # finding 17
        write(self.ws / "knowledge/archive/old.md", "# Old\n\nSee `decisions/missing.md`.\n")
        self.assertFalse(any("archive/old.md" in m for _, m in L.knowledge_upkeep(self.ws, R)))

    def test_case_variants_of_the_archive_count(self):  # finding 15
        self.assertTrue(L.archived("knowledge/ARCHIVE/note.md"))


class TestSecrets(Case):
    def test_no_secrets_in_proposals_or_reasons(self):  # finding 3
        with self.assertRaises(L.Refusal):
            L.delegate(self.ws, "tidy headings", "draft", "pass" + "word: SyntheticSecret123", today=TODAY)
        write(self.ws / "knowledge/n.md", "# N\n")
        with self.assertRaises(L.Refusal):
            L.compost(self.ws, "knowledge/n.md", "pass" + "word: SyntheticSecret123")


class TestDelegation(Case):
    def test_an_amendment_to_a_lower_level_wins(self):  # finding 4
        L.delegate(self.ws, "tidy headings", "bounded", "e", scope="headings in knowledge/", review="2026-11-30",
                   apply=True, today=TODAY)
        self.approve_all()
        k = L.delegations(self.ws, TODAY)[0][3]
        L.propose(self.ws, "exception", "Lower it", "Delegation: tidy headings = observe.", "owner", target=k, apply=True)
        self.approve_all()
        [(work, level, rest, k2, due)] = L.delegations(self.ws, TODAY)
        self.assertEqual(level, "observe")
        self.assertIn("(amended)", rest)

    def test_a_new_level_replaces_the_old_delegation(self):  # finding 5
        L.delegate(self.ws, "weekly drafts", "draft", "e", apply=True, today=TODAY)
        self.approve_all()
        rel, text = L.delegate(self.ws, "Weekly Drafts", "act-with-approval", "e", apply=True, today=TODAY)
        self.assertIn("kind: replace", text)
        self.approve_all()
        self.assertEqual([lv for _, lv, *_ in L.delegations(self.ws, TODAY)], ["act-with-approval"])

    def test_review_dates_are_validated_and_stored_in_one_form(self):  # findings 6, 7, 8
        for review in ("2026-02-30", "20261130"):
            with self.subTest(review=review), self.assertRaises(L.Refusal):
                L.delegate(self.ws, "tidy", "draft", "e", review=review, today=TODAY)
        with self.assertRaises(L.Refusal):
            L.delegate(self.ws, "tidy", "bounded", "e", scope="headings only. Look again on 2099-01-01",
                       review="2026-11-30", today=TODAY)

    def test_an_unreadable_date_in_a_decision_does_not_crash(self):  # finding 6
        write(self.ws / "decisions/2026-10-01-d.md", "---\nstatus: approved\n---\n\n# D\n\n## Rule\n\n"
              "Delegation: tidy = bounded. Look again on 2026-02-30.\n")
        self.assertTrue(L.delegations(self.ws, TODAY)[0][4])
        L.status(self.ws)
        L.agency(self.ws)

    def test_keyword_check_catches_synonyms_and_spares_harmless_words(self):  # finding 12
        with self.assertRaises(L.Refusal):
            L.delegate(self.ws, "erase duplicate files", "bounded", "e", scope="knowledge/", review="2026-11-30", today=TODAY)
        L.delegate(self.ws, "classify signal readings", "bounded", "e", scope="projects/", review="2026-11-30", today=TODAY)


class TestAgency(Case):
    def test_a_hook_that_does_not_run_the_guard_on_writes_is_not_enforcement(self):  # finding 13
        (self.ws / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Read", "hooks": [{"type": "command", "command": "echo tools/guard.py"}]}]}}), encoding="utf-8")
        self.assertFalse(L.hook_runs_guard(self.ws / ".claude/settings.json"))
        self.assertNotIn("runs in Claude Code and", L.agency(self.ws))

    def test_wording_does_not_claim_review_is_the_only_way(self):  # finding 14
        text = L.agency(self.ws)
        self.assertNotIn("Only `tools/review.py review` turns", text)
        self.assertIn("A person can still write a decision by hand", text)


class TestUpgradeAtlasShare(Case):
    @unittest.skipIf(os.name == "nt", "links need extra rights on Windows")
    def test_upgrade_never_writes_through_a_linked_me_folder(self):  # finding 9
        (self.ws / L.AGREEMENT_FILE).unlink()
        manifest = json.loads((self.ws / ".living/manifest.json").read_text(encoding="utf-8"))
        del manifest["files"][L.AGREEMENT_FILE]
        (self.ws / ".living/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        outside = self.base / "outside"
        outside.mkdir()
        for f in (self.ws / "me").iterdir():
            f.rename(outside / f.name)
        (self.ws / "me").rmdir()
        (self.ws / "me").symlink_to(outside)
        try:
            L.upgrade(self.ws, apply=True)
        except L.Refusal:
            pass
        self.assertFalse((outside / "agreement.md").exists())

    @unittest.skipIf(os.name == "nt", "links need extra rights on Windows")
    def test_atlas_does_not_follow_linked_folders(self):  # finding 10
        private = self.base / "private"
        write(private / "secret-client-plan.md", "See `decisions/x.md`.\n")
        for f in (self.ws / "projects").glob("*"):
            f.unlink()
        if (self.ws / "projects").exists():
            (self.ws / "projects").rmdir()
        (self.ws / "projects").symlink_to(private)
        self.assertNotIn("secret-client-plan", L.atlas(self.ws))

    def test_relative_markdown_links_count(self):  # finding 16
        write(self.ws / "proposals/2026-10-20-reports.md", "---\nstatus: proposed\nkind: new\ntarget: none\nevidence: e\n"
              "proposed_by: a\ndate: 2026-10-20\n---\n\n# Proposal: Reports\n\n## Proposed future state\n\n> Reports.\n\n"
              "## Why and open questions\n\nt\n")
        self.approve_all()
        k = R.current_decisions(self.ws)[0]
        write(self.ws / "projects/report.md", f"# Report\n\n[Applicable rule](../{k})\n")
        self.assertIn("used by `projects/report.md`", L.atlas(self.ws))

    def test_atlas_counts_reserved_names_only_at_the_top(self):  # finding 19
        write(self.ws / "knowledge/topic/README.md", "# Topic\n")
        write(self.ws / "knowledge/topic/inbox.md", "# Inbox\n")
        self.assertIn("- 3 file(s) in use", L.atlas(self.ws))  # the template's file plus these two

    def test_sharing_keeps_the_confidence_warning(self):  # finding 11
        org = L.init(self.base / "org", "manager", "en", team=True)
        me = L.init(self.base / "me2", "employee", "en")
        L.link(me, org, "sales")
        write(me / "knowledge/lead.md", "---\nconfidence: low\n---\n\n# Lead\n\nMaybe.\n")
        _, text = L.share(me, "knowledge/lead.md")
        self.assertIn("confidence: low", text)

    def test_agreement_names_real_switches(self):  # finding 20
        for lang in ("", "i18n/de/", "i18n/pl/"):
            text = (REPO / f"core/{lang}template/me/agreement.md").read_text(encoding="utf-8")
            with self.subTest(lang=lang):
                self.assertIn("living.py focus . on", text)
                self.assertIn(".living/profile.json", text)


if __name__ == "__main__":
    unittest.main()

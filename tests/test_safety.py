"""Regression tests from the second review: links, races, partial writes and doctor accuracy.

Each test names the failure it guards against. A refusal must leave the workspace exactly as it was.
"""
import json, os, shutil, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import living as L
import review as R


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
    """File bytes, folders and links, so leftover folders or replaced links count as changes."""
    out = {}
    for p in sorted(Path(root).rglob("*")):
        rel = str(p.relative_to(root))
        if p.is_symlink():
            out[rel + "@"] = os.readlink(p).encode()
        elif p.is_dir():
            out[rel + "/"] = b""
        else:
            out[rel] = p.read_bytes()
    return out


def make_module(root, mid, files, routing=None):
    d = Path(root) / mid
    for rel, text in files.items():
        (d / "files" / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / "files" / rel).write_text(text, encoding="utf-8", newline="\n")
    (d / "module.json").write_text(json.dumps({
        "id": mid, "version": "0.1.0", "kind": "workflow", "summary": "s", "requires": [],
        "routing": routing or [["need", next(iter(files))]], "needs_approval": [], "signals": []}))


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.ws = L.init(self.base / "ws", "manager", "en")
        self.outside = self.base / "outside"
        self.outside.mkdir()
        (self.outside / "keep.md").write_text("keep me\n", encoding="utf-8", newline="\n")

    def tearDown(self):
        self.tmp.cleanup()

    def refused(self, fn, *args, **kw):
        before = snapshot(self.ws), snapshot(self.outside)
        with self.assertRaises(L.Refusal):
            fn(*args, **kw)
        self.assertEqual((snapshot(self.ws), snapshot(self.outside)), before)


@unittest.skipUnless(CAN_LINK, "this system cannot create links")
class TestLinks(Case):
    def test_add_does_not_write_through_a_linked_folder(self):
        shutil.rmtree(self.ws / "workflows")
        (self.ws / "workflows").symlink_to(self.outside)
        self.refused(L.add_module, self.ws, "weekly-update", apply=True)

    def test_new_workflow_does_not_write_through_a_linked_folder(self):
        shutil.rmtree(self.ws / "workflows")
        (self.ws / "workflows").symlink_to(self.ws / "decisions")
        self.refused(L.new_workflow, self.ws, "plan", ["a"], apply=True)

    def test_remove_does_not_delete_through_a_linked_folder(self):
        L.add_module(self.ws, "staged-learning", apply=True)
        (self.ws / "lessons").rename(self.ws / "projects/lessons")
        (self.ws / "lessons").symlink_to(self.ws / "projects/lessons")
        self.refused(L.remove_module, self.ws, "staged-learning", apply=True)

    def test_linked_routing_file_is_never_written(self):
        (self.ws / "CONTEXT-ROUTING.md").unlink()
        (self.ws / "CONTEXT-ROUTING.md").symlink_to(self.ws / "SYSTEM.md")
        self.refused(L.add_module, self.ws, "weekly-update", apply=True)

    def test_planted_manifest_temp_link_is_not_followed(self):
        (self.ws / ".living/.manifest.json.tmp").symlink_to(self.outside / "keep.md")
        L.add_module(self.ws, "weekly-update", apply=True)
        self.assertEqual((self.outside / "keep.md").read_text(), "keep me\n")
        self.assertFalse((self.ws / ".living/manifest.json").is_symlink())

    def test_review_refuses_linked_proposals_and_decisions_folders(self):
        prop = self.ws / "proposals/2026-10-20-x.md"
        prop.write_text("---\nstatus: proposed\nkind: new\ntarget: none\nevidence: e\nproposed_by: a\n"
                        "date: 2026-10-20\n---\n\n# Proposal: X\n\n## Proposed future state\n\n> Rule.\n\n"
                        "## Why and open questions\n\nq\n")
        moved = self.base / "props"
        (self.ws / "proposals").rename(moved)
        (self.ws / "proposals").symlink_to(moved)
        with self.assertRaises(R.Refusal):
            R.review(self.ws, "proposals/2026-10-20-x.md", "approve", "Owner", date="2026-10-21")
        (self.ws / "proposals").unlink()
        moved.rename(self.ws / "proposals")
        shutil.rmtree(self.ws / "decisions")
        (self.ws / "decisions").symlink_to(self.outside)
        before = snapshot(self.outside)
        with self.assertRaises(R.Refusal):
            R.review(self.ws, "proposals/2026-10-20-x.md", "approve", "Owner", date="2026-10-21")
        self.assertEqual(snapshot(self.outside), before)


class TestModuleRules(Case):
    def test_modules_cannot_ship_agent_instructions_or_protected_aliases(self):
        mods = self.base / "mods"
        bad = {"override": "workflows/x/AGENTS.override.md", "local": "workflows/x/CLAUDE.local.md",
               "lower": "workflows/x/agents.md", "claudedir": ".claude/rules/extra.md",
               "codexdir": "workflows/.codex/x.md", "case": "Decisions/new.md", "dot": "workflows/x./a.md",
               "space": "workflows/x /a.md", "colon": "workflows/x:y.md"}
        for mid, rel in bad.items():
            with self.subTest(module=mid):
                make_module(mods, mid, {rel: "x\n"})
                with self.assertRaises(L.Refusal):
                    L.load_module(mid, mods)

    def test_routing_cells_must_be_one_line(self):
        mods = self.base / "mods"
        make_module(mods, "cr", {"workflows/c/CONTEXT.md": "c\n"}, routing=[["need\r\r## Heading", "workflows/c/CONTEXT.md"]])
        with self.assertRaises(L.Refusal):
            L.load_module("cr", mods)

    def test_manifest_cannot_point_removal_at_human_files(self):
        L.add_module(self.ws, "weekly-update", apply=True)
        mine = self.ws / "projects/mine.md"
        mine.write_text("my project\n", encoding="utf-8", newline="\n")
        m = json.loads((self.ws / ".living/manifest.json").read_text())
        m["modules"]["weekly-update"]["files"]["projects/mine.md"] = L.sha256(mine)
        (self.ws / ".living/manifest.json").write_text(json.dumps(m), encoding="utf-8", newline="\n")
        self.refused(L.remove_module, self.ws, "weekly-update", apply=True)
        self.assertEqual(mine.read_text(), "my project\n")


class TestAtomicity(Case):
    def test_file_edited_during_removal_is_kept(self):
        L.add_module(self.ws, "staged-learning", apply=True)
        real = L.routing_without

        def edit_meanwhile(text, mid):
            (self.ws / "lessons/active.md").write_text("## Active lessons\n\n- saved while removing\n", encoding="utf-8", newline="\n")
            return real(text, mid)

        with mock.patch.object(L, "routing_without", edit_meanwhile):
            delete, keep, _ = L.remove_module(self.ws, "staged-learning", apply=True)
        self.assertIn("lessons/active.md", keep)
        self.assertIn("saved while removing", (self.ws / "lessons/active.md").read_text())

    def test_failed_removal_restores_everything(self):
        L.add_module(self.ws, "staged-learning", apply=True)
        before = snapshot(self.ws)
        with mock.patch.object(L, "write_json", side_effect=OSError("disk full (simulated)")):
            with self.assertRaises(OSError):
                L.remove_module(self.ws, "staged-learning", apply=True)
        self.assertEqual(snapshot(self.ws), before)

    def test_partial_file_write_during_install_is_rolled_back(self):
        before = snapshot(self.ws)
        real = os.fdopen

        class Broken:
            def __init__(self, f): self.f = f
            def __enter__(self): return self
            def __exit__(self, *a): self.f.close()
            def write(self, data):
                self.f.write(data[:7])
                raise OSError("disk full (simulated)")

        with mock.patch.object(L.os, "fdopen", side_effect=lambda fd, *a, **k: Broken(real(fd, *a, **k))):
            with self.assertRaises(OSError):
                L.add_module(self.ws, "weekly-update", apply=True)
        self.assertEqual(snapshot(self.ws), before)

    def test_rollback_keeps_folders_that_existed_before(self):
        (self.ws / "lessons").mkdir()
        before = snapshot(self.ws)
        with mock.patch.object(L, "write_json", side_effect=OSError("simulated")):
            with self.assertRaises(OSError):
                L.add_module(self.ws, "staged-learning", apply=True)
        self.assertEqual(snapshot(self.ws), before)
        L.add_module(self.ws, "staged-learning", apply=True)
        L.remove_module(self.ws, "staged-learning", apply=True)
        self.assertTrue((self.ws / "lessons").is_dir(), "a folder the human made stays after removal")

    def test_parallel_changes_are_refused_while_locked(self):
        (self.ws / ".living/.lock").write_text("", encoding="utf-8", newline="\n")
        self.refused(L.add_module, self.ws, "weekly-update", apply=True)
        self.assertEqual(len(L.add_module(self.ws, "weekly-update")), 1, "a dry run still works")
        (self.ws / ".living/.lock").unlink()
        L.add_module(self.ws, "weekly-update", apply=True)
        (self.ws / ".living/.lock").write_text("", encoding="utf-8", newline="\n")
        self.refused(L.remove_module, self.ws, "weekly-update", apply=True)

    def test_human_note_in_modules_section_survives_last_removal(self):
        L.add_module(self.ws, "weekly-update", apply=True)
        r = self.ws / "CONTEXT-ROUTING.md"
        r.write_text(r.read_text().replace(L.ROUTING_END, "My own note about modules.\n\n" + L.ROUTING_END), encoding="utf-8", newline="\n")
        L.remove_module(self.ws, "weekly-update", apply=True)
        self.assertIn("My own note about modules.", r.read_text())

    def test_decision_that_appears_during_review_is_not_overwritten(self):
        prop = self.ws / "proposals/2026-10-20-x.md"
        prop.write_text("---\nstatus: proposed\nkind: new\ntarget: none\nevidence: e\nproposed_by: a\n"
                        "date: 2026-10-20\n---\n\n# Proposal: X\n\n## Proposed future state\n\n> Rule.\n\n"
                        "## Why and open questions\n\nq\n")
        real = R.build_new_decision

        def appears(root, *a):
            rel, text = real(root, *a)
            (root / rel).write_text("written by a human meanwhile\n", encoding="utf-8", newline="\n")
            return rel, text

        with mock.patch.object(R, "build_new_decision", appears):
            with self.assertRaises(R.Refusal):
                R.review(self.ws, "proposals/2026-10-20-x.md", "approve", "Owner", date="2026-10-21")
        self.assertEqual((self.ws / "decisions/2026-10-21-x.md").read_text(), "written by a human meanwhile\n")
        self.assertIn("status: proposed", prop.read_text())

    def test_quoted_code_fence_in_rule_is_refused(self):
        with self.assertRaises(R.Refusal):
            R.single_blockquote("> ```\n> Example only.", "p")


class TestDoctorAccuracy(Case):
    def approve_drafts(self):
        for f in ("SYSTEM.md", "PRINCIPLES.md"):
            p = self.ws / f
            p.write_text(p.read_text().replace("status: draft", "status: approved", 1), encoding="utf-8", newline="\n")

    def text(self):
        return L.format_doctor(L.doctor(self.ws))

    def test_broken_module_route_and_missing_tool_are_errors(self):
        self.approve_drafts()
        L.add_module(self.ws, "weekly-update", apply=True)
        r = self.ws / "CONTEXT-ROUTING.md"
        r.write_text(r.read_text().replace("workflows/weekly-update/CONTEXT.md", "workflows/weekly-update/NOT-HERE.md"), encoding="utf-8", newline="\n")
        (self.ws / "tools/review.py").unlink()
        t = self.text()
        self.assertIn("sends agents to workflows/weekly-update/NOT-HERE.md", t)
        self.assertIn("ERROR: tools/review.py is missing", t)

    def test_status_need_not_be_the_first_field(self):
        self.approve_drafts()
        p = self.ws / "SYSTEM.md"
        p.write_text(p.read_text().replace("---\nstatus: approved\n", "---\nreviewed_by: Owner\nstatus: approved\n", 1), encoding="utf-8", newline="\n")
        self.assertNotIn("SYSTEM.md is not approved", self.text())

    def test_damaged_manifest_gives_a_readable_refusal(self):
        (self.ws / ".living/manifest.json").write_text("{", encoding="utf-8", newline="\n")
        with self.assertRaises(L.Refusal) as e:
            L.doctor(self.ws)
        self.assertIn("damaged", str(e.exception))

    def test_copied_demo_file_without_banner_is_found(self):
        shutil.copy(REPO / "demo/moss-and-circuit/knowledge/services.md", self.ws / "knowledge/services.md")
        self.assertIn("ERROR: knowledge/services.md: demo sandbox content", self.text())

    def test_sub_bullets_are_not_counted_as_lessons(self):
        L.add_module(self.ws, "staged-learning", apply=True)
        (self.ws / "lessons/active.md").write_text(
            "## Active lessons\n\n" + "".join(f"- lesson {i}\n  - evidence {i}\n" for i in range(11)))
        self.assertNotIn("lessons/active.md has", self.text())

    def test_other_instruction_files_are_found(self):
        (self.ws / "workflows/x").mkdir()
        (self.ws / "workflows/x/AGENTS.override.md").write_text("x\n", encoding="utf-8", newline="\n")
        (self.ws / "workflows/x/.claude").mkdir()
        (self.ws / "workflows/x/.claude/rules.md").write_text("x\n", encoding="utf-8", newline="\n")
        (self.ws / "AGENTS.override.md").write_text("x\n", encoding="utf-8", newline="\n")
        t = self.text()
        self.assertIn("ERROR: workflows/x/AGENTS.override.md", t)
        self.assertIn("ERROR: workflows/x/.claude/rules.md", t)
        self.assertIn("WARN: AGENTS.override.md", t)


if __name__ == "__main__":
    unittest.main()

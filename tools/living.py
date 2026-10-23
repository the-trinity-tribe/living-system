#!/usr/bin/env python3
"""Create and inspect a Living System workspace. Standard library only.

  living.py init <dir> --profile <p> --language <code> [--calm-replies]
  living.py value-score <workspace>
  living.py modules [--workspace <ws>]
  living.py add <ws> <module> [--apply]
  living.py remove <ws> <module> [--apply]
  living.py new-workflow <ws> <name> --stages a,b,c [--goal "..."] [--apply]
  living.py doctor <ws>

`init` writes into a NEW folder, built in a temporary folder next to it and renamed
at the end, so a failure never leaves a half-made workspace.

`add` and `remove` only print a plan unless `--apply` is given. `add` never overwrites
a file. `remove` deletes only files that are unchanged since they were added.
"""
import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

KERNEL_VERSION = "0.2.0-dev"
PROFILES = ("student", "professional", "employee", "manager")
MARKER = "<!-- profile:append -->"
HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "core"


class Refusal(Exception):
    """Raised when init must not proceed. Nothing is left behind."""


def check_target(target):
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise Refusal(f"{target} exists and is not a folder")
    if target.is_dir() and any(target.iterdir()):
        raise Refusal(f"{target} is not empty; choose a new or empty folder")
    if not target.parent.is_dir():
        raise Refusal(f"parent folder {target.parent} does not exist")
    if HERE.parent in (target.resolve(), *target.resolve().parents):
        raise Refusal("the workspace must be outside the Living System repository folder")


def copy_tree(src, dst):
    for p in sorted(src.rglob("*")):
        rel = p.relative_to(src)
        if p.is_dir():
            (dst / rel).mkdir(parents=True, exist_ok=True)
        elif not p.name.endswith(".append.md"):
            if p.name == "gitignore":  # stored without the dot so git does not apply it inside this repo
                rel = rel.with_name(".gitignore")
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dst / rel)


def apply_appends(profile_dir, dst):
    """`X.append.md` in a profile is inserted into X at the marker, or added at the end."""
    for p in sorted(profile_dir.rglob("*.append.md")):
        rel = p.relative_to(profile_dir)
        base = dst / rel.parent / (p.name[: -len(".append.md")] + ".md")
        text, add = base.read_text(encoding="utf-8"), p.read_text(encoding="utf-8")
        text = text.replace(MARKER, add.rstrip("\n") + "\n" + MARKER, 1) if MARKER in text else text.rstrip("\n") + "\n" + add
        base.write_text(text, encoding="utf-8")


def strip_markers(dst):
    for p in dst.rglob("*.md"):
        t = p.read_text(encoding="utf-8")
        if MARKER in t:
            p.write_text(t.replace(MARKER + "\n", "").replace(MARKER, ""), encoding="utf-8")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_manifest(ws):
    files = {p.relative_to(ws).as_posix(): sha256(p)
             for p in sorted(ws.rglob("*")) if p.is_file() and p.name != "manifest.json"}
    (ws / ".living" / "manifest.json").write_text(
        json.dumps({"kernel_version": KERNEL_VERSION, "files": files}, indent=2) + "\n", encoding="utf-8")


def build(ws, profile, language, calm_replies):
    copy_tree(CORE / "template", ws)
    copy_tree(CORE / "profiles" / profile, ws)
    apply_appends(CORE / "profiles" / profile, ws)
    strip_markers(ws)
    (ws / "tools").mkdir()
    shutil.copyfile(HERE / "review.py", ws / "tools" / "review.py")
    (ws / ".living").mkdir()
    (ws / ".living" / "profile.json").write_text(json.dumps(
        {"profile": profile, "language": language, "calm_replies": bool(calm_replies)}, indent=2) + "\n",
        encoding="utf-8")
    (ws / ".living" / "catalog.md").write_text(catalog_text(), encoding="utf-8")
    write_manifest(ws)


def catalog_text(root=None):
    """A snapshot of the optional modules, so an agent in the workspace knows what exists."""
    root = root or MODULES
    mods = [load_module(d.name, root) for d in sorted(Path(root).iterdir()) if (d / "module.json").is_file()] \
        if Path(root).is_dir() else []
    rows = "".join(f"| `{m['id']}` | {m['summary']} | {', '.join(m['signals'])} |\n" for m in mods)
    return ("# Optional modules you can add\n\n"
            "Not installed unless they appear under \"Installed modules\" in `CONTEXT-ROUTING.md`. This list is a "
            "snapshot from when the workspace was created; the Living System folder may have more.\n\n"
            "| Module | What it gives you | May help when the human keeps asking about |\n| --- | --- | --- |\n"
            f"{rows or '| (none) | | |' + chr(10)}\n"
            "To see what a module would add, run `python3 <Living System folder>/tools/living.py add . <module>` "
            "inside this workspace. Nothing is written without `--apply`, and only after the human says yes "
            "(`AGENTS.md` section 11).\n")


def init(target, profile, language, calm_replies=False):
    if profile not in PROFILES:
        raise Refusal(f"profile must be one of {', '.join(PROFILES)}")
    if not re.fullmatch(r"[a-z]{2,3}(-[A-Za-z0-9]{2,8})?", language):
        raise Refusal("language must be a code like en, de, pl or pt-BR")
    target = Path(target).expanduser()
    check_target(target)
    tmp = Path(tempfile.mkdtemp(prefix=".living-init-", dir=target.parent))
    try:
        umask = os.umask(0)
        os.umask(umask)
        os.chmod(tmp, 0o777 & ~umask)
        build(tmp, profile, language, calm_replies)
        emptied = target.is_dir()
        if emptied:
            target.rmdir()  # Windows cannot rename onto an existing folder, even an empty one
        try:
            os.rename(tmp, target)
        except BaseException:
            if emptied:
                target.mkdir(exist_ok=True)
            raise
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return target


SCORES = ("right", "wrong", "made up", "don't know")


def value_score(ws):
    path = Path(ws) / "value-check" / "questions.md"
    if not path.is_file():
        raise Refusal(f"{path} not found")
    counts = {"before": dict.fromkeys(SCORES, 0), "after": dict.fromkeys(SCORES, 0)}
    unscored = {"before": 0, "after": 0}
    cols = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        low = [c.lower() for c in cells]
        if "before" in low and "after" in low:
            cols = {"before": low.index("before"), "after": low.index("after")}
            continue
        if cols is None or set("".join(cells)) <= set("-: "):
            continue
        for which, i in cols.items():
            v = cells[i].strip("`").lower().replace("’", "'") if i < len(cells) else ""
            if v in counts[which]:
                counts[which][v] += 1
            elif v == "":
                unscored[which] += 1
            else:
                raise Refusal(f"{path}: '{cells[i]}' is not one of: {', '.join(SCORES)}")
    if cols is None:
        raise Refusal(f"{path}: no table with 'Before' and 'After' columns found")
    return counts, unscored


def format_score(counts, unscored):
    head = f"{'':8}" + "".join(f"{s:>11}" for s in SCORES)
    rows = [f"{w:<8}" + "".join(f"{counts[w][s]:>11}" for s in SCORES) for w in ("before", "after")]
    notes = [f"{w}: {n} not scored yet" for w, n in unscored.items() if n]
    return "\n".join([head, *rows, *notes])


MODULES = HERE.parent / "modules"
MODULE_KINDS = ("workflow", "knowledge", "skill", "domain")
MODULE_ID = r"[a-z0-9][a-z0-9-]{0,40}"
# Owned by the human or the kernel; a module may never ship or delete files here (compared case-insensitively).
PROTECTED_DIRS = ("decisions", "proposals", "projects", "me", ".living", "tools")
ROOT_FILES = ("context-routing.md", "system.md", "principles.md", "readme.md", ".gitignore")
# Files that Claude Code, Codex or similar agents load automatically as instructions.
INSTRUCTION_NAMES = ("agents.md", "agents.override.md", "claude.md", "claude.local.md", "gemini.md")
UNSAFE = re.compile(r"[\x00-\x1f\x7f\x85  ]")
ROUTING_START, ROUTING_END = "<!-- modules:start -->", "<!-- modules:end -->"
ROUTING_INTRO = ("## Installed modules\n\nOptional modules you added. The file each row points to says what "
                 "that module may do.\n\n| Need | Read |\n| --- | --- |\n")


def path_problem(rel):
    """Why a module may not own this workspace path, or None. Used for module files and manifest entries."""
    parts = rel.split("/") if isinstance(rel, str) else [""]
    low = [part.lower() for part in parts]
    if (not rel or rel.startswith("/") or "\\" in rel or ":" in rel or UNSAFE.search(rel)
            or any(part in ("", ".", "..") or part != part.rstrip(". ") for part in parts)):
        return "is not a plain relative path"
    if low[0] in PROTECTED_DIRS:
        return "is in a folder owned by you or the kernel"
    if len(parts) == 1 and low[0] in ROOT_FILES:
        return "is a workspace root file"
    if low[-1] in INSTRUCTION_NAMES or any(part.startswith(".") for part in parts[:-1]) \
            or (parts[-1].startswith(".") and parts[-1] != ".gitkeep"):
        return "is an agent instruction file or a hidden tool folder"
    return None


def linked_part(ws, rel):
    """The first existing link on the way from the workspace to rel, or None."""
    cur = Path(ws)
    for part in rel.split("/"):
        cur = cur / part
        if cur.is_symlink():
            return cur.relative_to(ws).as_posix()
        if not cur.exists():
            return None
    return None


def refuse_links(ws, rels):
    for rel in rels:
        link = linked_part(ws, rel)
        if link:
            raise Refusal(f"{link} is a link; Living System does not write or delete through links. Nothing was changed")


def load_module(mid, root=MODULES):
    """Read and validate modules/<mid>/. Refuses anything a module must not do."""
    if not re.fullmatch(MODULE_ID, mid):
        raise Refusal(f"{mid!r} is not a valid module id")
    d = Path(root) / mid
    try:
        meta = json.loads((d / "module.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise Refusal(f"no module named {mid!r}") from None
    except json.JSONDecodeError as e:
        raise Refusal(f"modules/{mid}/module.json is not valid JSON: {e}") from None
    for key, kind in (("id", str), ("version", str), ("kind", str), ("summary", str),
                      ("requires", list), ("routing", list), ("needs_approval", list), ("signals", list)):
        if not isinstance(meta.get(key), kind):
            raise Refusal(f"modules/{mid}/module.json: '{key}' missing or not a {kind.__name__}")
    if meta["id"] != mid or meta["kind"] not in MODULE_KINDS:
        raise Refusal(f"modules/{mid}/module.json: id must be {mid!r} and kind one of {', '.join(MODULE_KINDS)}")
    files = sorted(p.relative_to(d / "files").as_posix() for p in (d / "files").rglob("*") if p.is_file())
    if not files:
        raise Refusal(f"modules/{mid} has no files to install")
    for rel in files:
        why = path_problem(rel)
        if why:
            raise Refusal(f"modules/{mid}: may not ship {rel}: it {why}")
    for row in meta["routing"]:
        if (not isinstance(row, list) or len(row) != 2 or row[1] not in files
                or any(not isinstance(c, str) or "|" in c or UNSAFE.search(c) for c in row)):
            raise Refusal(f"modules/{mid}: routing row {row!r} must be [one-line need, one of its own files]")
    return {**meta, "dir": d, "files": files}


def read_manifest(ws):
    path = Path(ws) / ".living" / "manifest.json"
    if not path.is_file():
        raise Refusal(f"{ws} is not a Living System workspace (no .living/manifest.json)")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise Refusal(f".living/manifest.json is damaged ({e}); restore it from a backup or git") from None
    mods = data.get("modules", {}) if isinstance(data, dict) else None
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict) or not isinstance(mods, dict) \
            or not all(isinstance(m, dict) and isinstance(m.get("files"), dict) for m in mods.values()):
        raise Refusal(".living/manifest.json has an unexpected structure; restore it from a backup or git")
    return data


def write_json(path, data):
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2) + "\n")
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


@contextlib.contextmanager
def workspace_lock(ws):
    """One add or remove at a time per workspace, so changes cannot overwrite each other."""
    lock = Path(ws) / ".living" / ".lock"
    try:
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        raise Refusal("another Living System command is changing this workspace (.living/.lock exists). "
                      "If none is running, delete that file and try again") from None
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def install_order(mid, root=MODULES, trail=()):
    """The module and everything it requires, dependencies first."""
    if mid in trail:
        raise Refusal(f"module dependency loop: {' -> '.join(trail + (mid,))}")
    m = load_module(mid, root)
    out = []
    for dep in m["requires"]:
        out += [x for x in install_order(dep, root, trail + (mid,)) if x["id"] not in {y["id"] for y in out}]
    return out + [m]


def plan_add(ws, mid, root=MODULES):
    ws = Path(ws)
    installed = read_manifest(ws).get("modules", {})
    if mid in installed:
        raise Refusal(f"module {mid!r} is already installed")
    order = [m for m in install_order(mid, root) if m["id"] not in installed]
    seen, problems = {}, []
    for m in order:
        for rel in m["files"]:
            link = linked_part(ws, rel)
            if link:
                problems.append(f"{link} is a link (module {m['id']}); Living System does not write through links")
            elif (ws / rel).exists():
                problems.append(f"{rel} already exists (module {m['id']})")
            elif rel in seen:
                problems.append(f"{rel} is shipped by both {seen[rel]} and {m['id']}")
            seen[rel] = m["id"]
    if problems:
        raise Refusal("nothing was installed:\n  " + "\n  ".join(problems))
    return order


def format_add_plan(order, mid):
    lines = []
    for m in order:
        why = "" if m["id"] == mid else f" (required by {mid})"
        lines += [f"Module {m['id']} {m['version']} ({m['kind']}){why}: {m['summary']}",
                  "  Adds files:", *(f"    {rel}" for rel in m["files"]),
                  "  Adds routing rows:", *(f"    {need} -> {path}" for need, path in m["routing"])]
        if m["needs_approval"]:
            lines += ["  Always needs your approval:", *(f"    {a}" for a in m["needs_approval"])]
    return "\n".join(lines)


def routing_with(text, m):
    rows = "".join(f"| {need} | `{path}` <!-- module:{m['id']} --> |\n" for need, path in m["routing"])
    if ROUTING_START not in text:
        text = text.rstrip("\n") + f"\n\n{ROUTING_START}\n{ROUTING_INTRO}\n{ROUTING_END}\n"
    head, tail = text.split(ROUTING_END, 1)
    return head.rstrip("\n") + "\n" + rows + "\n" + ROUTING_END + tail


def routing_without(text, mid):
    text = "".join(l for l in text.splitlines(True) if f"<!-- module:{mid} -->" not in l)
    if ROUTING_START in text and ROUTING_END in text:
        head, rest = text.split(ROUTING_START, 1)
        inner, tail = rest.split(ROUTING_END, 1)
        if inner.strip() == ROUTING_INTRO.strip():  # only our own wrapper is left, so drop it
            text = head.rstrip("\n") + "\n" + tail.lstrip("\n")
    return text


def routing_file(ws):
    routing = Path(ws) / "CONTEXT-ROUTING.md"
    if routing.is_symlink() or not routing.is_file():
        raise Refusal("CONTEXT-ROUTING.md is missing or is a link; nothing was changed")
    return routing


def add_module(ws, mid, apply=False, root=MODULES):
    ws = Path(ws)
    if not apply:
        return plan_add(ws, mid, root)
    read_manifest(ws)
    with workspace_lock(ws):
        order = plan_add(ws, mid, root)
        routing = routing_file(ws)
        old_routing = routing.read_text(encoding="utf-8")
        manifest = read_manifest(ws)
        created, made = [], []
        try:
            new_routing = old_routing
            for m in order:
                dirs = []
                for rel in m["files"]:
                    dst = ws / rel
                    for d in reversed([dst.parent, *dst.parent.parents]):
                        if ws in d.parents and not d.exists():
                            d.mkdir()
                            made.append(d)
                            dirs.append(d.relative_to(ws).as_posix())
                    fd = os.open(dst, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
                    created.append(dst)
                    with os.fdopen(fd, "wb") as f:
                        f.write((m["dir"] / "files" / rel).read_bytes())
                new_routing = routing_with(new_routing, m)
                manifest.setdefault("modules", {})[m["id"]] = {
                    "version": m["version"], "kind": m["kind"], "requires": m["requires"],
                    "files": {rel: sha256(ws / rel) for rel in m["files"]}, "dirs": dirs}
            routing.write_text(new_routing, encoding="utf-8")
            write_json(ws / ".living" / "manifest.json", manifest)
        except BaseException:
            for p in reversed(created):
                p.unlink(missing_ok=True)
            for d in reversed(made):
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()
            routing.write_text(old_routing, encoding="utf-8")
            raise
    return order


def plan_remove(ws, mid):
    ws = Path(ws)
    installed = read_manifest(ws).get("modules", {})
    if mid not in installed:
        raise Refusal(f"module {mid!r} is not installed")
    needed_by = sorted(k for k, v in installed.items() if mid in v.get("requires", []))
    if needed_by:
        raise Refusal(f"module {mid!r} is required by {', '.join(needed_by)}; remove those first")
    entry = installed[mid]
    for rel in [*entry["files"], *entry.get("dirs", [])]:
        why = path_problem(rel) if rel in entry["files"] else (path_problem(rel + "/x") or None)
        if why:
            raise Refusal(f".living/manifest.json lists {rel!r} for {mid}, which {why}; nothing was changed")
    refuse_links(ws, entry["files"])
    delete, keep, missing = [], [], []
    for rel, digest in sorted(entry["files"].items()):
        p = ws / rel
        if not p.is_file():
            missing.append(rel)
        elif sha256(p) == digest:
            delete.append(rel)
        else:
            keep.append(rel)
    return delete, keep, missing


def format_remove_plan(mid, delete, keep, missing):
    lines = [f"Module {mid}:", "  Deletes (unchanged since added):", *([f"    {r}" for r in delete] or ["    (none)"])]
    if keep:
        lines += ["  Keeps (you edited these, so they are yours now):", *(f"    {r}" for r in keep)]
    if missing:
        lines += ["  Already gone:", *(f"    {r}" for r in missing)]
    lines.append("  Removes its rows from CONTEXT-ROUTING.md. Never touches decisions/, proposals/ or projects/.")
    return "\n".join(lines)


def remove_module(ws, mid, apply=False):
    ws = Path(ws)
    if not apply:
        return plan_remove(ws, mid)
    read_manifest(ws)
    with workspace_lock(ws):
        delete, keep, missing = plan_remove(ws, mid)
        manifest = read_manifest(ws)
        entry = manifest["modules"][mid]
        routing = routing_file(ws)
        old_routing = routing.read_text(encoding="utf-8")
        backups, removed_dirs = {}, []
        try:
            routing.write_text(routing_without(old_routing, mid), encoding="utf-8")
            for rel in list(delete):
                p = ws / rel
                data = p.read_bytes()
                if hashlib.sha256(data).hexdigest() != entry["files"][rel]:  # edited since the plan: keep it
                    delete.remove(rel)
                    keep.append(rel)
                    continue
                backups[p] = data
                p.unlink()
            for rel in sorted(entry.get("dirs", []), key=lambda r: -r.count("/")):
                d = ws / rel
                if d.is_dir() and not d.is_symlink() and not any(d.iterdir()):
                    d.rmdir()
                    removed_dirs.append(d)
            del manifest["modules"][mid]
            if not manifest["modules"]:
                del manifest["modules"]
            write_json(ws / ".living" / "manifest.json", manifest)
        except BaseException:
            for d in reversed(removed_dirs):
                d.mkdir(exist_ok=True)
            for p, data in backups.items():
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            routing.write_text(old_routing, encoding="utf-8")
            raise
    return delete, sorted(keep), missing


def list_modules(root=MODULES, ws=None):
    installed = read_manifest(ws).get("modules", {}) if ws else {}
    mods = [load_module(d.name, root) for d in sorted(Path(root).iterdir()) if (d / "module.json").is_file()] \
        if Path(root).is_dir() else []
    lines = []
    for m in mods:
        mark = "[installed] " if m["id"] in installed else ""
        lines.append(f"{mark}{m['id']} ({m['kind']}): {m['summary']}")
        if ws and m["id"] not in installed:
            lines.append(f"    may help when you mention: {', '.join(m['signals'])}")
    return "\n".join(lines) or "No modules available."


FILL = "<fill in:"  # marks text the agent and human still have to write; `doctor` lists what is left


def workflow_files(slug, stages, goal):
    """Text of every file in a new staged workflow (ICM-style), keyed by path inside the workflow."""
    folders = [f"{i:02d}-{s}" for i, s in enumerate(stages, 1)]
    rows = "".join(f"| {i} | `{f}/` | {FILL} what this stage does> | `{f}/output/<date>-{s}.md` |\n"
                   for i, (f, s) in enumerate(zip(folders, stages), 1))
    files = {"CONTEXT.md": (
        f"# Workflow: {slug.replace('-', ' ')}\n\n"
        f"Staged workflow in the style of Interpretable Context Methodology (ICM). It is working context, "
        f"not authority. It cannot change any rule.\n\n"
        f"Goal: {goal or FILL + ' one sentence: what this workflow produces, for whom>'}\n\n"
        f"## Stages\n\n| Stage | Folder | What happens | Output |\n| --- | --- | --- | --- |\n{rows}\n"
        f"Run one stage at a time. Open only that stage's `CONTEXT.md`. The human checks and may edit each "
        f"result before the next stage starts. The next stage uses the edited file.\n\n"
        f"## Decisions that apply\n\n- {FILL} current decisions this work must follow, or \"none yet\">. "
        f"Check with `python3 tools/review.py current`.\n\n"
        f"## Never do\n\n- Never send, publish or share anything. A human does that.\n"
        f"- Never invent facts, dates, numbers or commitments. Missing means \"not recorded\".\n"
        f"- Never edit `decisions/`, `SYSTEM.md` or `PRINCIPLES.md`.\n\n"
        f"## Shared reference\n\n- `references/`: stable material every run uses (formats, tone, checklists).\n"),
        "references/.gitkeep": ""}
    for i, (folder, stage) in enumerate(zip(folders, stages)):
        source = ("| Human | The request | What this run is about | Sets the scope |" if i == 0 else
                  f"| Previous stage | the newest file in `{folders[i - 1]}/output/` | All, as the human edited it "
                  f"| The input to this stage |")
        files[f"{folder}/CONTEXT.md"] = (
            f"# Stage {i + 1}: {stage.replace('-', ' ')}\n\n{FILL} one sentence: the single job of this stage>\n\n"
            f"## Inputs\n\n| Source | File | Scope | Why |\n| --- | --- | --- | --- |\n{source}\n\n"
            f"## Process\n\n1. Read only the inputs above.\n2. {FILL} the steps of this stage>\n"
            f"3. Mark anything not recorded in the inputs as \"not recorded\".\n\n"
            f"## Outputs\n\n| Artifact | Location | Format |\n| --- | --- | --- |\n"
            f"| {FILL} artifact> | `{folder}/output/<date>-{stage}.md` | Markdown |\n\n"
            f"## Checkpoint\n\n| After step | Agent presents | Human decides |\n| --- | --- | --- |\n"
            f"| 3 | The output file | Edit it, then start the next stage, or stop |\n")
        files[f"{folder}/output/.gitkeep"] = ""
    return files


def new_workflow(ws, slug, stages, goal="", apply=False):
    ws = Path(ws)
    read_manifest(ws)
    if not re.fullmatch(MODULE_ID, slug):
        raise Refusal(f"{slug!r} is not a valid workflow name (lowercase letters, digits and hyphens)")
    if not 1 <= len(stages) <= 9 or len(set(stages)) != len(stages) \
            or not all(re.fullmatch(MODULE_ID, s) for s in stages):
        raise Refusal("give 1 to 9 different stage names (lowercase letters, digits and hyphens)")
    if "\n" in goal or "|" in goal:
        raise Refusal("the goal must be one line without '|'")
    target = ws / "workflows" / slug
    refuse_links(ws, [f"workflows/{slug}"])
    if target.exists():
        raise Refusal(f"workflows/{slug} already exists")
    files = workflow_files(slug, stages, goal)
    if apply:
        (ws / "workflows").mkdir(exist_ok=True)
        tmp = Path(tempfile.mkdtemp(prefix=f".{slug}-", dir=ws / "workflows"))
        try:
            for rel, text in files.items():
                (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
                (tmp / rel).write_text(text, encoding="utf-8")
            os.rename(tmp, target)
        except BaseException:
            shutil.rmtree(tmp, ignore_errors=True)
            raise
    return sorted(f"workflows/{slug}/{rel}" for rel in files)


DEMO_BANNER = "DEMO — fictional sandbox"
MAX_LESSONS = 20


def review_tool():
    import importlib.util
    spec = importlib.util.spec_from_file_location("living_review", HERE / "review.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


AGENT_DIRS = (".claude", ".codex", ".agents", ".cursor")


def demo_fingerprints():
    """Hashes of files that only the demo ships, so a copied demo file is recognised even without its banner."""
    def hashes(folder):
        return {sha256(p) for p in folder.rglob("*") if p.is_file()} if folder.is_dir() else set()
    shared = hashes(CORE) | hashes(MODULES)
    return {h for h in hashes(HERE.parent / "demo") - shared if h != sha256_bytes(b"")}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def doctor(ws):
    """Read-only health check. Returns (level, message) pairs; level is ERROR, WARN or INFO."""
    ws = Path(ws)
    manifest = read_manifest(ws)
    R = review_tool()
    out = [("ERROR", p) for p in R.check(ws)]
    files = [p for p in sorted(ws.rglob("*")) if p.is_file() and ".git" not in p.relative_to(ws).parts]
    demo = demo_fingerprints()
    for p in files:
        rel = p.relative_to(ws).as_posix()
        name, below_root = p.name.lower(), p.parent != ws
        if name in INSTRUCTION_NAMES and below_root:
            out.append(("ERROR", f"{rel}: agent instruction file below the workspace root; agents may load it "
                                 f"as a competing rule set. Move its content into a CONTEXT.md"))
        elif name in ("agents.override.md", "claude.local.md") and not below_root:
            out.append(("WARN", f"{rel}: personal or override instructions; some agents read it instead of or "
                                f"on top of AGENTS.md. Make sure it does not contradict AGENTS.md"))
        if any(part.lower() in AGENT_DIRS for part in p.relative_to(ws).parts[1:-1]):
            out.append(("ERROR", f"{rel}: agent settings folder below the workspace root; agents may load it"))
        if sha256(p) in demo or (p.suffix == ".md" and DEMO_BANNER in p.read_text(encoding="utf-8", errors="replace")):
            out.append(("ERROR", f"{rel}: demo sandbox content; keep demo material out of your workspace"))
    kernel = manifest.get("files", {})
    tool = ws / "tools/review.py"
    if "tools/review.py" in kernel and not tool.is_file():
        out.append(("ERROR", "tools/review.py is missing; the review commands in AGENTS.md cannot run. "
                             "Copy it back from the Living System folder"))
    elif "tools/review.py" in kernel and sha256(tool) != kernel["tools/review.py"]:
        out.append(("WARN", "tools/review.py differs from the version installed; the review rules may not "
                            "behave as documented"))
    routing = (ws / "CONTEXT-ROUTING.md").read_text(encoding="utf-8") if (ws / "CONTEXT-ROUTING.md").is_file() else ""
    installed = manifest.get("modules", {})
    routed = {}
    for need, path, mid in re.findall(r"^\|([^|]*)\|\s*`([^`]+)`\s*<!-- module:([a-z0-9-]+) -->\s*\|", routing, re.M):
        routed.setdefault(mid, []).append(path)
    for mid in sorted(set(installed) - set(routed)):
        out.append(("ERROR", f"module {mid} is installed but has no row in CONTEXT-ROUTING.md"))
    for mid in sorted(set(routed) - set(installed)):
        out.append(("ERROR", f"CONTEXT-ROUTING.md has rows for module {mid}, which is not installed"))
    for mid, paths in sorted(routed.items()):
        for path in paths:
            if not (ws / path).is_file():
                out.append(("ERROR", f"CONTEXT-ROUTING.md sends agents to {path} for module {mid}, but it does not exist"))
    for mid, entry in sorted(installed.items()):
        gone = [r for r in entry.get("files", {}) if not (ws / r).is_file()]
        if gone:
            out.append(("WARN", f"module {mid}: {len(gone)} file(s) missing, e.g. {gone[0]}"))
    for f in ("SYSTEM.md", "PRINCIPLES.md"):
        if (ws / f).is_file():
            try:
                status = R.split_frontmatter((ws / f).read_text(encoding="utf-8"), f)[0].get("status")
            except R.Refusal:
                status = None
            if status != "approved":
                out.append(("WARN", f"{f} is not approved yet, so agents treat it as a draft, not as your rules"))
    for p in sorted((ws / "workflows").rglob("CONTEXT.md")) if (ws / "workflows").is_dir() else []:
        rel, text = p.relative_to(ws).as_posix(), p.read_text(encoding="utf-8", errors="replace")
        if len(text.splitlines()) >= 80:
            out.append(("WARN", f"{rel} has {len(text.splitlines())} lines; keep stage files under 80"))
        if FILL in text:
            out.append(("WARN", f"{rel} still has {text.count(FILL)} '{FILL} ...>' part(s) to write"))
    active = ws / "lessons/active.md"
    if active.is_file():
        body = active.read_text(encoding="utf-8", errors="replace").split("## Active lessons", 1)[-1]
        n = len(re.findall(r"^(?:[-*]|\d+\.) \S", body, re.M))  # top-level entries only, not sub-bullets
        if n > MAX_LESSONS:
            out.append(("WARN", f"lessons/active.md has {n} lessons; the limit is {MAX_LESSONS}. Merge or retire some"))
    for p in sorted((ws / "proposals").glob("*.md")) if (ws / "proposals").is_dir() else []:
        try:
            meta, _, _ = R.split_frontmatter(p.read_text(encoding="utf-8"), p.name)
        except (R.Refusal, UnicodeDecodeError):
            continue
        if meta.get("status") in R.REVIEWABLE:
            out.append(("INFO", f"proposals/{p.name} is {meta['status']} and waits for your review"))
    return out


def format_doctor(results):
    if not results:
        return "All good: no problems found."
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    lines = [f"{lvl}: {msg}" for lvl, msg in sorted(results, key=lambda r: order[r[0]])]
    counts = {lvl: sum(1 for l, _ in results if l == lvl) for lvl in order}
    return "\n".join(lines + [f"{counts['ERROR']} error(s), {counts['WARN']} warning(s), {counts['INFO']} note(s)."])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init", help="create a new workspace in a new folder")
    i.add_argument("dir")
    i.add_argument("--profile", required=True, choices=PROFILES)
    i.add_argument("--language", required=True)
    i.add_argument("--calm-replies", action="store_true")
    v = sub.add_parser("value-score", help="count right/wrong/made up/don't know in value-check/questions.md")
    v.add_argument("workspace")
    ls = sub.add_parser("modules", help="list optional modules")
    ls.add_argument("--workspace")
    for name, text in (("add", "plan (or with --apply, install) a module"),
                       ("remove", "plan (or with --apply, remove) a module")):
        p = sub.add_parser(name, help=text)
        p.add_argument("workspace")
        p.add_argument("module")
        p.add_argument("--apply", action="store_true")
    w = sub.add_parser("new-workflow", help="plan (or with --apply, create) a staged workflow folder")
    w.add_argument("workspace")
    w.add_argument("name")
    w.add_argument("--stages", required=True, help="comma-separated stage names in order, e.g. research,draft,review")
    w.add_argument("--goal", default="")
    w.add_argument("--apply", action="store_true")
    d = sub.add_parser("doctor", help="read-only health check of a workspace")
    d.add_argument("workspace")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "init":
            ws = init(a.dir, a.profile, a.language, a.calm_replies)
            print(f"Created workspace: {ws.resolve()}")
            print(f"Profile: {a.profile} | language: {a.language} | calm replies: {'on' if a.calm_replies else 'off'}")
            print("Undo: delete that folder. Next: open it in Claude Code or Codex.")
        elif a.cmd == "value-score":
            print(format_score(*value_score(a.workspace)))
        elif a.cmd == "modules":
            print(list_modules(ws=a.workspace))
        elif a.cmd == "add":
            print(format_add_plan(add_module(a.workspace, a.module, a.apply), a.module))
            print("Installed." if a.apply else "Nothing was written. Run again with --apply to install.")
        elif a.cmd == "remove":
            print(format_remove_plan(a.module, *remove_module(a.workspace, a.module, a.apply)))
            print("Removed." if a.apply else "Nothing was changed. Run again with --apply to remove.")
        elif a.cmd == "doctor":
            results = doctor(a.workspace)
            print(format_doctor(results))
            return 1 if any(lvl == "ERROR" for lvl, _ in results) else 0
        else:
            stages = [s.strip() for s in a.stages.split(",") if s.strip()]
            paths = new_workflow(a.workspace, a.name, stages, a.goal, a.apply)
            print(f"Workflow {a.name}: {len(stages)} stages\n" + "\n".join(f"  {p}" for p in paths))
            print(f"Created. Next: fill in every '{FILL} ...>' with the human." if a.apply
                  else "Nothing was written. Run again with --apply to create.")
    except Refusal as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

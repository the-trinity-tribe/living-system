#!/usr/bin/env python3
"""Create and inspect a Living System workspace. Standard library only.

  living.py init <dir> --profile <p> --language <code> [--calm-replies] [--coach]
  living.py value-score <workspace>
  living.py modules [--workspace <ws>]
  living.py add <ws> <module> [--apply]
  living.py remove <ws> <module> [--apply]
  living.py new-workflow <ws> <name> --stages a,b,c [--goal "..."] [--apply]
  living.py doctor <ws>
  living.py status <ws>
  living.py since <ws> --date YYYY-MM-DD | --days N
  living.py handbook <ws> [--out FILE]
  living.py scan <ws> [paths...]
  living.py export <ws> <file.zip> [--apply]
  living.py protect <ws> [--apply]
  living.py runs <ws> [--add NAME | --decide NAME automate|manual|later | --forget NAME]
  living.py propose <ws> --kind new|exception|replace|retire --title ... --rule ... --evidence ... [--apply]
  living.py upgrade <ws> [--apply]

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

KERNEL_VERSION = "0.2.0"
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


def copy_tree(src, dst, translation=False):
    for p in sorted(src.rglob("*")):
        if translation and p.name in NOT_TRANSLATED:
            continue
        rel = p.relative_to(src)
        if p.is_dir():
            continue  # folders are created for the files inside them
        elif not p.name.endswith(".append.md"):
            if p.name == "gitignore":  # stored without the dot so git does not apply it inside this repo
                rel = rel.with_name(".gitignore")
            # dot-claude/ and dot-codex/ become .claude/ and .codex/: this repository ignores those folders in git
            rel = Path(*["." + part[4:] if part.startswith("dot-") else part for part in rel.parts])
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dst / rel)


I18N = CORE / "i18n"
# Agent instruction files stay English in every language: one tested rule set. The agent still replies and
# writes new content in the chosen language (AGENTS.md section 8).
NOT_TRANSLATED = ("AGENTS.md", "AGENTS.append.md", "CLAUDE.md", "gitignore")


def language_dir(language):
    """core/i18n/<language>, or the base language (de for de-AT), or None for English starter files."""
    for code in dict.fromkeys((language.lower(), language.split("-")[0].lower())):
        if (I18N / code).is_dir():
            return I18N / code
    return None


def apply_appends(profile_dir, dst, translated_dir=None):
    """`X.append.md` in a profile is inserted into X at the marker, or added at the end."""
    for p in sorted(profile_dir.rglob("*.append.md")):
        rel = p.relative_to(profile_dir)
        base = dst / rel.parent / (p.name[: -len(".append.md")] + ".md")
        src = translated_dir / rel if translated_dir and (translated_dir / rel).is_file() \
            and p.name not in NOT_TRANSLATED else p
        text, add = base.read_text(encoding="utf-8"), src.read_text(encoding="utf-8")
        text = text.replace(MARKER, add.rstrip("\n") + "\n" + MARKER, 1) if MARKER in text else text.rstrip("\n") + "\n" + add
        base.write_text(text, encoding="utf-8", newline="\n")


def strip_markers(dst):
    for p in dst.rglob("*.md"):
        t = p.read_text(encoding="utf-8")
        if MARKER in t:
            p.write_text(t.replace(MARKER + "\n", "").replace(MARKER, ""), encoding="utf-8", newline="\n")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_manifest(ws):
    files = {p.relative_to(ws).as_posix(): sha256(p)
             for p in sorted(ws.rglob("*")) if p.is_file() and p.name != "manifest.json"}
    (ws / ".living" / "manifest.json").write_text(
        json.dumps({"kernel_version": KERNEL_VERSION, "files": files}, indent=2) + "\n", encoding="utf-8", newline="\n")


def build(ws, profile, language, calm_replies, coach=False):
    lang = language_dir(language)
    copy_tree(CORE / "template", ws)
    if lang and (lang / "template").is_dir():
        copy_tree(lang / "template", ws, translation=True)
    copy_tree(CORE / "profiles" / profile, ws)
    translated_profile = lang / "profiles" / profile if lang else None
    if translated_profile and translated_profile.is_dir():
        copy_tree(translated_profile, ws, translation=True)
    apply_appends(CORE / "profiles" / profile, ws, translated_profile)
    strip_markers(ws)
    for skill in sorted((CORE / "skills").glob("*/SKILL.md")) if (CORE / "skills").is_dir() else []:
        # One source, two places: Claude Code reads .claude/skills, Codex reads .agents/skills.
        for agent_dir in (".claude/skills", ".agents/skills"):
            dst = ws / agent_dir / skill.parent.name / "SKILL.md"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(skill, dst)
    (ws / "tools").mkdir()
    shutil.copyfile(HERE / "review.py", ws / "tools" / "review.py")
    shutil.copyfile(HERE / "guard.py", ws / "tools" / "guard.py")
    (ws / ".living").mkdir()
    (ws / ".living" / "profile.json").write_text(json.dumps(
        {"profile": profile, "language": language, "calm_replies": bool(calm_replies), "coach": bool(coach)}, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    (ws / ".living" / "catalog.md").write_text(catalog_text(), encoding="utf-8", newline="\n")
    # Where the tools live on this computer, so agents can run status, runs or doctor without asking.
    # Listed in .gitignore: it contains a local path.
    (ws / ".living" / "local.json").write_text(json.dumps({"product_folder": str(HERE.parent)}, indent=2) + "\n",
                                                 encoding="utf-8", newline="\n")
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


def init(target, profile, language, calm_replies=False, coach=False):
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
        build(tmp, profile, language, calm_replies, coach)
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
# Column names and score words in the translated starter files; results are counted under the English names.
COLUMN_WORDS = {"before": ("before", "vorher", "przed"), "after": ("after", "nachher", "po")}
SCORE_WORDS = {word: score for score, words in {
    "right": ("right", "richtig", "dobrze"), "wrong": ("wrong", "falsch", "\u017ale"),
    "made up": ("made up", "erfunden", "zmy\u015blone"),
    "don't know": ("don't know", "wei\u00df nicht", "weiss nicht", "nie wiem")}.items() for word in words}


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
        found = {which: next((i for i, c in enumerate(low) if c in words), None) for which, words in COLUMN_WORDS.items()}
        if None not in found.values():
            cols = found
            continue
        if cols is None or set("".join(cells)) <= set("-: "):
            continue
        for which, i in cols.items():
            v = cells[i].strip("`").lower().replace("’", "'") if i < len(cells) else ""
            if v in SCORE_WORDS:
                counts[which][SCORE_WORDS[v]] += 1
            elif v == "":
                unscored[which] += 1
            else:
                raise Refusal(f"{path}: '{cells[i]}' is not a score word; use one of: {', '.join(SCORE_WORDS)}")
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
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
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
        old_routing = check_markers(routing.read_text(encoding="utf-8"))
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
                    "files": {rel: sha256(ws / rel) for rel in m["files"]}, "dirs": dirs, "routing": m["routing"]}
            routing.write_text(new_routing, encoding="utf-8", newline="\n")
            write_json(ws / ".living" / "manifest.json", manifest)
        except BaseException:
            for p in reversed(created):
                p.unlink(missing_ok=True)
            for d in reversed(made):
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()
            routing.write_text(old_routing, encoding="utf-8", newline="\n")
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
        old_routing = check_markers(routing.read_text(encoding="utf-8"))
        backups, removed_dirs = {}, []
        try:
            routing.write_text(routing_without(old_routing, mid), encoding="utf-8", newline="\n")
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
            routing.write_text(old_routing, encoding="utf-8", newline="\n")
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


# Folders and files that belong to the human; upgrade never writes them.
UPGRADE_SKIP_DIRS = ("decisions/", "proposals/", "projects/", "me/", ".living/upgrade/")
UPGRADE_SKIP_FILES = (".living/profile.json", ".living/manifest.json", ".living/local.json")
UPGRADE_COPIES = ".living/upgrade"


def local_folder(ws):
    """product_folder from .living/local.json, or None if the file is missing or damaged."""
    try:
        data = json.loads((Path(ws) / ".living/local.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    folder = data.get("product_folder") if isinstance(data, dict) else None
    return folder if isinstance(folder, str) and folder else None


def check_markers(text):
    """Refuse a routing file whose modules section markers are damaged, so nothing makes it worse."""
    s, e = text.count(ROUTING_START), text.count(ROUTING_END)
    if (s, e) not in ((0, 0), (1, 1)) or (s and text.index(ROUTING_START) > text.index(ROUTING_END)):
        raise Refusal(f"CONTEXT-ROUTING.md has damaged module markers ({ROUTING_START} and {ROUTING_END} must "
                      f"appear once each, start first). Fix them and try again; nothing was changed")
    return text


def without_modules_block(text):
    """The routing text as the template wrote it: the modules section (owned by add/remove) taken out."""
    if ROUTING_START in text and ROUTING_END in text:
        head, rest = text.split(ROUTING_START, 1)
        return head.rstrip("\n") + "\n" + rest.split(ROUTING_END, 1)[1].lstrip("\n")
    return text


def modules_block(text):
    if ROUTING_START in text and ROUTING_END in text:
        return ROUTING_START + text.split(ROUTING_START, 1)[1].split(ROUTING_END, 1)[0] + ROUTING_END + "\n"
    return ""


def module_rows(mid, routing):
    return [f"| {need} | `{path}` <!-- module:{mid} --> |" for need, path in routing]


class Plan(list):
    """Upgrade steps as (action, path, new bytes, owner) plus what each file looked like when planned."""
    def __init__(self):
        super().__init__()
        self.expect = {}         # path -> sha256 of the file when planned, or None if it did not exist
        self.routing_hash = None  # sha256 of CONTEXT-ROUTING.md when planned


def classify(current, new_bytes, installed_hash):
    """What upgrade does with one file: add, gone (you deleted it), same, unowned (yours, already equal),
    update (you never changed it) or keep (you changed it, or it was never ours)."""
    if current is None:
        return "gone" if installed_hash else "add"
    if current == new_bytes:
        return "same" if installed_hash else "unowned"
    return "update" if installed_hash and sha256_bytes(current) == installed_hash else "keep"


def plan_upgrade(ws):
    """Every product-owned file the current Living System would change, and how. Read-only."""
    ws = Path(ws)
    manifest = read_manifest(ws)
    try:
        prof = json.loads((ws / ".living/profile.json").read_text(encoding="utf-8"))
        profile, language, calm = prof["profile"], prof["language"], bool(prof.get("calm_replies"))
        coach = bool(prof.get("coach"))
    except (OSError, ValueError, KeyError, TypeError):
        raise Refusal(".living/profile.json is missing or damaged; upgrade needs it to know your profile") from None
    if profile not in PROFILES:
        raise Refusal(f".living/profile.json names an unknown profile {profile!r}")
    routing_path = ws / "CONTEXT-ROUTING.md"
    routing = check_markers(routing_path.read_text(encoding="utf-8")) if routing_path.is_file() else ""
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "ws"
        fresh.mkdir()
        build(fresh, profile, language, calm, coach)
        template = {p.relative_to(fresh).as_posix(): p.read_bytes() for p in sorted(fresh.rglob("*")) if p.is_file()}
    plan = Plan()
    plan.routing_hash = sha256_bytes(routing.encode("utf-8")) if routing_path.is_file() else None

    def step(rel, data, installed, owner, current=None, exists=None):
        p = ws / rel
        if exists is None:
            exists = p.is_file()
            current = p.read_bytes() if exists else None
        action = classify(current if exists else None, data, installed)
        if action == "add" and (p.exists() or p.is_symlink()):
            action = "keep"
        plan.expect[rel] = sha256_bytes(p.read_bytes()) if p.is_file() else None
        plan.append((action, rel, data, owner))

    for rel, data in template.items():
        if rel in UPGRADE_SKIP_FILES or rel.startswith(UPGRADE_SKIP_DIRS):
            continue
        refuse_links(ws, [rel, f"{UPGRADE_COPIES}/{rel}"])
        if rel == "CONTEXT-ROUTING.md" and routing_path.is_file():
            step(rel, data, manifest["files"].get(rel), None,
                 without_modules_block(routing).encode("utf-8"), exists=True)
        else:
            step(rel, data, manifest["files"].get(rel), None)
    local = ws / ".living/local.json"
    known = local_folder(ws)
    if known != str(HERE.parent):  # this computer's Living System folder, not content: always kept current
        plan.append(("local", ".living/local.json", template[".living/local.json"], None))
    installed_mods = manifest.get("modules", {})
    for mid, entry in sorted(installed_mods.items()):
        try:
            m = load_module(mid)
        except Refusal:
            plan.append(("module-gone", mid, None, mid))
            continue
        missing = [d for d in m["requires"] if d not in installed_mods]
        if missing:
            raise Refusal(f"module {mid} now requires {', '.join(missing)}, which is not installed. Add it first "
                          f"(living.py add <workspace> {missing[0]}), then run upgrade again; nothing was changed")
        refuse_links(ws, m["files"] + [f"{UPGRADE_COPIES}/{r}" for r in m["files"]])
        for rel in m["files"]:
            step(rel, (m["dir"] / "files" / rel).read_bytes(), entry["files"].get(rel), mid)
        have = [l for l in routing.splitlines() if f"<!-- module:{mid} -->" in l]
        want = module_rows(mid, m["routing"])
        if have != want:
            old = module_rows(mid, entry["routing"]) if "routing" in entry else None
            plan.append(("routing" if old is None or have == old else "routing-kept", mid, None, mid))
    return plan


def format_upgrade_plan(plan):
    groups = [("update", "Updates (you never changed these)"), ("add", "Adds (new in this version)"),
              ("keep", f"Keeps your version; the new one is saved in {UPGRADE_COPIES}/ to compare"),
              ("gone", "You deleted these; they stay deleted"), ("routing", "Refreshes routing rows for module"),
              ("routing-kept", f"Keeps your edited routing rows for module; the new rows are saved in "
                               f"{UPGRADE_COPIES}/CONTEXT-ROUTING.<module>.md"),
              ("module-gone", "Installed module no longer available here; left as it is"),
              ("local", "Records where Living System is on this computer")]
    lines = []
    for action, title in groups:
        items = [rel for a, rel, _, _ in plan if a == action]
        if items:
            lines += [f"{title}:", *(f"  {r}" for r in items)]
    if not lines:
        return "Already up to date."
    return "\n".join(lines + ["Never touched: decisions/, proposals/, projects/, me/ and your setup choices."])


def upgrade(ws, apply=False):
    ws = Path(ws)
    if not apply:
        return plan_upgrade(ws)
    read_manifest(ws)
    with workspace_lock(ws):
        plan = plan_upgrade(ws)
        manifest = read_manifest(ws)
        written, made = {}, []  # path -> (bytes before, bytes we wrote); folders we created

        def changed_meanwhile(rel):
            raise Refusal(f"{rel} changed while upgrading. Nothing was changed; run upgrade again")

        def put(rel, data, expect, owner=None):
            p = ws / rel
            now = p.read_bytes() if p.is_file() else None
            if (None if now is None else sha256_bytes(now)) != expect or (now is None and p.is_symlink()):
                changed_meanwhile(rel)
            for d in reversed([p.parent, *p.parent.parents]):
                if ws in d.parents and not d.exists():
                    d.mkdir()
                    made.append(d)
                    if owner:
                        manifest["modules"][owner].setdefault("dirs", []).append(d.relative_to(ws).as_posix())
            if now is None:
                fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
                written[p] = (None, data)
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                return
            fd, tmp = tempfile.mkstemp(prefix=f".{p.name}.", suffix=".tmp", dir=p.parent)
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                written.setdefault(p, (now, data))
                os.replace(tmp, p)
                written[p] = (written[p][0], data)
            except BaseException:
                Path(tmp).unlink(missing_ok=True)
                raise

        def put_copy(rel, data):
            p = ws / rel
            put(rel, data, sha256_bytes(p.read_bytes()) if p.is_file() else None)

        try:
            routing_update = None
            for action, rel, data, owner in plan:
                files = manifest["files"] if owner is None else manifest["modules"].get(owner, {}).get("files", {})
                if rel == "CONTEXT-ROUTING.md" and owner is None:
                    if action == "update":
                        routing_update = data
                    if action in ("update", "same"):
                        files[rel] = sha256_bytes(data)
                    elif action == "keep":
                        put_copy(f"{UPGRADE_COPIES}/{rel}", data)
                elif action in ("update", "add"):
                    put(rel, data, plan.expect[rel], owner)
                    files[rel] = sha256_bytes(data)
                elif action == "same":
                    files[rel] = sha256_bytes(data)
                elif action == "keep":
                    put_copy(f"{UPGRADE_COPIES}/{rel}", data)
                elif action == "local":
                    target = ws / rel
                    put(rel, data, sha256_bytes(target.read_bytes()) if target.is_file() else None)
            refresh = [mid for a, mid, _, _ in plan if a == "routing"]
            for mid in [m for a, m, _, _ in plan if a == "routing-kept"]:
                rows = module_rows(mid, load_module(mid)["routing"])
                put_copy(f"{UPGRADE_COPIES}/CONTEXT-ROUTING.{mid}.md", ("\n".join(rows) + "\n").encode("utf-8"))
            if routing_update is not None or refresh:
                routing = routing_file(ws)
                text = routing.read_text(encoding="utf-8")
                if sha256_bytes(text.encode("utf-8")) != plan.routing_hash:
                    changed_meanwhile("CONTEXT-ROUTING.md")
                if routing_update is not None:
                    block = modules_block(text)
                    text = routing_update.decode("utf-8").rstrip("\n") + ("\n\n" + block if block else "\n")
                for mid in refresh:
                    text = routing_with(routing_without(text, mid), load_module(mid))
                put("CONTEXT-ROUTING.md", text.encode("utf-8"), plan.routing_hash)
            for mid, entry in manifest.get("modules", {}).items():
                try:
                    m = load_module(mid)
                except Refusal:
                    continue
                entry.update(version=m["version"], kind=m["kind"], requires=m["requires"])
                if mid in refresh or "routing" not in entry:
                    entry["routing"] = m["routing"]
            manifest["kernel_version"] = KERNEL_VERSION
            write_json(ws / ".living" / "manifest.json", manifest)
        except BaseException:
            for p, (before, ours) in written.items():
                now = p.read_bytes() if p.is_file() else None
                if now != ours:
                    continue  # the human changed it after we wrote it: leave their version
                if before is None:
                    p.unlink()
                else:
                    p.write_bytes(before)
            for d in reversed(made):
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()
            raise
    return plan


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


RUNS_FILE = ".living/runs.json"
THIRD_RUN = 3
RUN_DECISIONS = ("automate", "manual", "later")
RUNS_ABOUT = ("Third-Run Rule counts: how often a kind of work came up. Only short names, dates and your decisions; "
              "never content or names of people or clients. Delete an entry with: living.py runs . --forget <name>")


def read_runs(ws):
    path = Path(ws) / RUNS_FILE
    if not path.is_file():
        return {"_about": RUNS_ABOUT, "work": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise Refusal(f"{RUNS_FILE} is damaged; delete it to start counting again") from None
    work = data.get("work") if isinstance(data, dict) else None
    ok = isinstance(work, dict) and all(
        isinstance(e, dict) and isinstance(e.get("count"), int) and e["count"] >= 0
        and isinstance(e.get("first"), str) and isinstance(e.get("last"), str)
        and e.get("decision") in (None,) + RUN_DECISIONS
        and isinstance(e.get("remind_after", 0), int) and re.fullmatch(MODULE_ID, str(name))
        for name, e in work.items())
    if not ok:
        raise Refusal(f"{RUNS_FILE} has an unexpected structure; delete it to start counting again")
    return data


def run_is_due(entry):
    """True when this kind of work has reached the third run and still waits for a human decision."""
    if entry["count"] < THIRD_RUN:
        return False
    if entry.get("decision") in (None, ""):
        return True
    return entry.get("decision") == "later" and entry["count"] >= entry.get("remind_after", 0)


def runs(ws, add=None, decide=None, decision=None, after=None, forget=None, date=None):
    """Count a kind of work, record the human's decision, or forget it. Returns (entries, message)."""
    import datetime
    ws = Path(ws)
    read_manifest(ws)
    name = add or decide or forget
    if name is None:
        return read_runs(ws)["work"], ""
    if not re.fullmatch(MODULE_ID, name):
        raise Refusal(f"{name!r} is not a short name (lowercase letters, digits and hyphens, e.g. weekly-update)")
    refuse_links(ws, [RUNS_FILE])
    date = date or datetime.date.today().isoformat()
    with workspace_lock(ws):
        data = read_runs(ws)
        work = data["work"]
        if add:
            others = sorted(n for n in work if n != name)
            new = name not in work
            e = work.setdefault(name, {"count": 0, "first": date, "last": date, "decision": None})
            e["count"] += 1
            e["last"] = date
            message = (f"{name}: run {e['count']}. " + (
                f"This is run {e['count']}: by the Third-Run Rule it is time to decide. Choose: automate "
                f"(a module or a workflow), manual (keep doing it by hand) or later (ask again after a few more runs). "
                f"Record it with: living.py runs . --decide {name} automate|manual|later" if run_is_due(e) else
                "Counted. Nothing else happens before the third run." if e["count"] < THIRD_RUN else
                f"Counted. You chose 'later'; you will be asked again at run {e['remind_after']}."
                if e.get("decision") == "later" else f"Counted. Your decision on record: {e['decision']}."))
            if new and others:
                message += (f"\nNew name. Already counted: {', '.join(others)}. If this is the same kind of work as one "
                            f"of those, undo with --forget {name} and count it under that name instead.")
        elif decide:
            if name not in work:
                raise Refusal(f"{name} has not been counted yet")
            if decision not in RUN_DECISIONS:
                raise Refusal(f"decision must be one of {', '.join(RUN_DECISIONS)}")
            e = work[name]
            e.update(decision=decision, decided=date)
            e.pop("remind_after", None)
            if decision == "later":
                e["remind_after"] = e["count"] + (after or 3)
            message = f"{name}: decision '{decision}' recorded" + (
                f"; you will be asked again at run {e['remind_after']}." if decision == "later" else ".")
        else:
            if name not in work:
                raise Refusal(f"{name} is not in {RUNS_FILE}")
            del work[name]
            message = f"{name}: forgotten."
        write_json(ws / RUNS_FILE, data)
    return work, message


def format_runs(work):
    if not work:
        return "Nothing counted yet."
    lines = []
    for name, e in sorted(work.items()):
        state = "decide now" if run_is_due(e) else (e.get("decision") or "counting")
        lines.append(f"{name}: {e['count']} run(s), first {e['first']}, last {e['last']}, {state}")
    return "\n".join(lines)


EXPORT_SKIP_FILES = (".living/local.json", ".living/.lock", ".review.lock")
EXPORT_SKIP_PARTS = (".git", "__pycache__")
EXPORT_NOTE = """Living System workspace export

These are plain Markdown and JSON files. Any text editor, and any AI tool that can read files, can open them.

To use them again: unzip this file into a new, empty folder. Then, from a Living System folder, run
    python3 tools/living.py doctor <that folder>
and, if the Living System version changed, python3 tools/living.py upgrade <that folder>.

Left out on purpose: .living/local.json (a path on the old computer), .living/.lock, .living/upgrade/,
.git/ and Python caches.
"""


def export_files(ws):
    ws = Path(ws)
    out = []
    for p in sorted(ws.rglob("*")):
        rel = p.relative_to(ws).as_posix()
        if p.is_symlink() or not p.is_file() or rel in EXPORT_SKIP_FILES or rel.startswith(".living/upgrade/") \
                or set(p.relative_to(ws).parts) & set(EXPORT_SKIP_PARTS):
            continue
        out.append(rel)
    return out


def export(ws, target, apply=False):
    """Pack the workspace into one zip file. Plan only unless apply. Never writes into the workspace."""
    import zipfile
    ws = Path(ws).resolve()
    read_manifest(ws)
    target = Path(target).expanduser().resolve()
    if target.suffix.lower() != ".zip":
        raise Refusal("the export file name must end in .zip")
    if ws in (target, *target.parents):
        raise Refusal("save the export outside the workspace, so it does not include itself")
    if target.exists() or target.is_symlink():
        raise Refusal(f"{target} already exists; choose a new file name")
    if not target.parent.is_dir():
        raise Refusal(f"folder {target.parent} does not exist")
    if not apply:
        return export_files(ws)
    R = review_tool()
    with workspace_lock(ws), R.review_lock(ws):  # no add, remove, upgrade or review half-way through the export
        files = export_files(ws)
        fd, tmp = tempfile.mkstemp(prefix=".living-export-", suffix=".zip", dir=target.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr("EXPORT-README.txt", EXPORT_NOTE)
                for rel in files:
                    z.writestr(rel, read_no_follow(ws / rel))
            try:
                os.link(tmp, target)  # fails if the name appeared meanwhile: never overwrite
            except FileExistsError:
                raise Refusal(f"{target} appeared while exporting; nothing was overwritten") from None
            except OSError:  # file systems without hard links
                if target.exists():
                    raise Refusal(f"{target} appeared while exporting; nothing was overwritten") from None
                os.replace(tmp, target)
        finally:
            Path(tmp).unlink(missing_ok=True)
    return files


def read_no_follow(path):
    """Read a regular file without following a link that may have appeared after listing it."""
    import stat as _stat
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0))
    except OSError as e:
        import errno
        if e.errno in (errno.ELOOP, getattr(errno, "EMLINK", -1)):
            raise Refusal(f"{path} changed into a link while exporting; nothing was written") from None
        raise
    try:
        if not _stat.S_ISREG(os.fstat(fd).st_mode) or Path(path).is_symlink():
            raise Refusal(f"{path} changed into a link or folder while exporting; nothing was written")
        with os.fdopen(fd, "rb") as f:
            fd = None
            return f.read()
    finally:
        if fd is not None:
            os.close(fd)


PROPOSE_KINDS = ("new", "exception", "replace", "retire")


def slugify(title):
    """A plain file-name part from a title in any language: 'Nur ich schicke Angebote' -> 'nur-ich-schicke-angebote'."""
    import unicodedata
    s = title.lower().replace("ß", "ss").replace("ł", "l")
    ascii_ = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    ascii_ = re.sub(r"[^a-z0-9]+", "-", ascii_).strip("-")[:50].strip("-")
    # titles in other scripts keep their letters: '只有我能发送报价' -> '只有我能发送报价'
    s = ascii_ if len(ascii_) >= 3 or not re.search(r"[^\W_]", s) else \
        re.sub(r"[\W_]+", "-", unicodedata.normalize("NFC", s)).strip("-")[:50].strip("-")
    if not s:
        raise Refusal("the title needs at least one letter or digit")
    return s


def propose(ws, kind, title, rule, evidence, why="", proposed_by="agent", target=None, date=None, apply=False):
    """Write a correctly formatted proposal (never a decision). Returns (path, text). Plan only unless apply."""
    import datetime
    ws = Path(ws)
    read_manifest(ws)
    R = review_tool()
    if kind not in PROPOSE_KINDS:
        raise Refusal(f"kind must be one of {', '.join(PROPOSE_KINDS)}")
    for value, what in ((title, "the title"), (evidence, "the evidence"), (proposed_by, "--by"), (target or "", "--target")):
        R.one_line(value, what)
    if not title.strip() or not rule.strip() or not evidence.strip():
        raise Refusal("a proposal needs a title, the rule (or for retire: the reason) and the evidence")
    if re.search(r"^\s*#", why, re.M):
        raise Refusal("the why text must not contain headings")
    date = date or datetime.date.today().isoformat()
    rel = f"proposals/{date}-{slugify(title)}.md"
    refuse_links(ws, [rel])
    if (ws / rel).exists():
        raise Refusal(f"{rel} already exists; choose another title")
    quote = "\n".join("> " + line.rstrip() if line.strip() else ">" for line in rule.strip().splitlines())
    why = why.strip() or "Not recorded yet. A human should add why this rule is wanted and anything still unclear."
    front = ["status: proposed"]
    if kind == "new":
        if target:
            raise Refusal("kind new has no target; it creates a first rule")
        front += ["kind: new", "target: none"]
        intro = "Not current truth. Nothing changes until a human approves it with `tools/review.py review`."
        middle = ""
    else:
        if not target:
            raise Refusal(f"kind {kind} needs --target: the current decision it changes")
        R.safe_rel(ws, target, "decisions/")
        if target not in R.current_decisions(ws):
            raise Refusal(f"{target} is not a current decision; `python3 tools/review.py current` lists them")
        _, _, tbody = R.split_frontmatter((ws / target).read_text(encoding="utf-8"), target)
        current = R.section(tbody, "Rule", target)
        front += [f"kind: {kind}", f"target: {target}", f"target_sha256: {R.sha256(ws / target)}"]
        intro = "Not current truth. The approved decision in `target` stays in force until a human approves a change."
        middle = ("## Current canonical state\n\n" + "\n".join("> " + l if l.strip() else ">" for l in current.splitlines())
                  + f"\n\n## New evidence\n\n{evidence.strip()}. Any attribution in it is not verified.\n\n")
    front += [f"evidence: {evidence.strip()}", f"proposed_by: {proposed_by.strip() or 'agent'}", f"date: {date}"]
    text = ("---\n" + "\n".join(front) + "\n---\n\n" + f"# Proposal: {title.strip()}\n\n{intro}\n\n" + middle
            + f"## Proposed future state\n\n{quote}\n\n## Why and open questions\n\n{why}\n")
    meta, _, body = R.split_frontmatter(text, rel)  # the same checks review.py will apply later
    R.proposal_kind(meta, rel)
    R.single_blockquote(R.section(body, "Proposed future state", rel), rel)
    if apply:
        (ws / "proposals").mkdir(exist_ok=True)
        fd = os.open(ws / rel, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(text.encode("utf-8"))
            problems = [x for x in R.check(ws) if rel in x]
            if problems:
                raise Refusal("the proposal did not pass check and was removed: " + "; ".join(problems))
        except BaseException:
            (ws / rel).unlink(missing_ok=True)
            raise
    return rel, text


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
                (tmp / rel).write_text(text, encoding="utf-8", newline="\n")
            os.rename(tmp, target)
        except BaseException:
            shutil.rmtree(tmp, ignore_errors=True)
            raise
    return sorted(f"workflows/{slug}/{rel}" for rel in files)


DEMO_BANNER = "DEMO — fictional sandbox"
STALE_DAYS = 90  # knowledge files last verified longer ago than this get a re-check reminder
KNOWLEDGE_SKIP = ("README.md", "inbox.md", "_template.md")


def knowledge_ages(ws, today=None):
    """(path, days since last_verified or None if missing, error or None) for each knowledge file."""
    import datetime
    R = review_tool()
    today = today or datetime.date.today()
    out = []
    for p in sorted((Path(ws) / "knowledge").rglob("*.md")) if (Path(ws) / "knowledge").is_dir() else []:
        if p.name in KNOWLEDGE_SKIP and p.parent == Path(ws) / "knowledge":
            continue
        rel = p.relative_to(ws).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---\n"):
            out.append((rel, None, None))
            continue
        try:
            value = R.split_frontmatter(text, rel)[0].get("last_verified")
        except Refusal as e:
            out.append((rel, None, str(e)))
            continue
        if value is None:
            out.append((rel, None, None))
            continue
        try:
            days = (today - datetime.date.fromisoformat(value)).days
        except ValueError:
            out.append((rel, None, f"last_verified {value!r} is not a date like 2026-10-24"))
            continue
        out.append((rel, days, "in the future" if days < 0 else None))
    return out
MAX_LESSONS = 20


def review_tool():
    import importlib.util
    spec = importlib.util.spec_from_file_location("living_review", HERE / "review.py")
    mod = importlib.util.module_from_spec(spec)
    saved, sys.dont_write_bytecode = sys.dont_write_bytecode, True  # read-only commands leave no cache files
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = saved
    mod.Refusal = Refusal  # one refusal type, so the CLI reports review.py's refusals as plain messages
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


GUARD_FILES = {"tools/guard.py": HERE / "guard.py", ".claude/settings.json": CORE / "template/dot-claude/settings.json",
               ".codex/hooks.json": CORE / "template/dot-codex/hooks.json"}


def hook_runs_guard(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        groups = data["hooks"]["PreToolUse"]
        return any("tools/guard.py" in h.get("command", "") for g in groups for h in g.get("hooks", []))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False


def guard_problems(ws, manifest):
    """Is the write guard in place and switched on for both agents?"""
    out = []
    installed = "tools/guard.py" in manifest.get("files", {})
    if not (ws / "tools/guard.py").is_file():
        if installed or any((ws / f).is_file() for f in (".claude/settings.json", ".codex/hooks.json")):
            out.append(("ERROR", "tools/guard.py is missing, so agents are not stopped from editing decisions/ "
                                 "directly. Restore it with: living.py protect <workspace> --apply"))
        return out
    for f, agent in ((".claude/settings.json", "Claude Code"), (".codex/hooks.json", "Codex")):
        if not (ws / f).is_file():
            out.append(("WARN", f"{f} is missing, so {agent} does not run the write guard. Restore it with: "
                                f"living.py protect <workspace> --apply"))
        elif not hook_runs_guard(ws / f):
            out.append(("WARN", f"{f} does not run tools/guard.py any more, so {agent} is not guarded. Compare it "
                                f"with the Living System template, or ask for help"))
    return out


def protect(ws, apply=False):
    """Put back a missing guard or hook file. Never overwrites an existing file. Returns the files it adds."""
    ws = Path(ws)
    read_manifest(ws)
    missing = [rel for rel in GUARD_FILES if not (ws / rel).exists()]
    refuse_links(ws, missing)
    if apply and missing:
        with workspace_lock(ws):
            manifest = read_manifest(ws)
            for rel_path in missing:
                dst = ws / rel_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                fd = os.open(dst, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
                with os.fdopen(fd, "wb") as f:
                    f.write(GUARD_FILES[rel_path].read_bytes())
                manifest["files"][rel_path] = sha256(dst)
            write_json(ws / ".living" / "manifest.json", manifest)
    return missing


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
    local = ws / ".living/local.json"
    if not local.is_file():
        out.append(("INFO", ".living/local.json is missing, so agents will ask where Living System is; run upgrade "
                            "from your Living System folder to record it"))
    if local.is_file():
        folder = local_folder(ws)
        if not folder or not (Path(folder) / "tools/living.py").is_file():
            out.append(("WARN", ".living/local.json does not point at a Living System folder on this computer; run "
                                "upgrade from your Living System folder to fix it, or edit product_folder"))
    for problem_level, message in guard_problems(ws, manifest):
        out.append((problem_level, message))
    kernel = manifest.get("files", {})
    tool = ws / "tools/review.py"
    if "tools/review.py" in kernel and not tool.is_file():
        out.append(("ERROR", "tools/review.py is missing; the review commands in AGENTS.md cannot run. "
                             "Copy it back from the Living System folder"))
    elif "tools/review.py" in kernel and sha256(tool) != kernel["tools/review.py"]:
        out.append(("WARN", "tools/review.py differs from the version installed; the review rules may not "
                            "behave as documented"))
    routing = (ws / "CONTEXT-ROUTING.md").read_text(encoding="utf-8") if (ws / "CONTEXT-ROUTING.md").is_file() else ""
    try:
        check_markers(routing)
    except Refusal as e:
        out.append(("ERROR", str(e).replace("Fix them and try again; nothing was changed", "Fix them before add, remove or upgrade")))
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
    knowledge_module = "knowledge-inbox" in installed
    for rel, days, problem in knowledge_ages(ws):
        if problem:
            out.append(("WARN", f"{rel}: {problem}"))
        elif days is not None and days > STALE_DAYS:
            out.append(("WARN", f"{rel} was last verified {days} days ago; check it is still true, then update last_verified"))
        elif days is None and knowledge_module:
            out.append(("INFO", f"{rel} has no last_verified date; add one after you check it"))
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
    if (ws / "decisions").is_dir():
        out += R.verify(ws)
    steering = set()
    for level, rel, line, what in scan(ws):
        if level == "ERROR" or what.startswith("invisible"):
            out.append((level, f"{rel}, line {line}: {what}"))
        else:
            steering.add(rel)
    if steering:
        out.append(("WARN", f"{len(steering)} file(s) contain text addressed to an AI, e.g. {sorted(steering)[0]}; "
                            f"run living.py scan for details"))
    return out


NEXT_STEP = r"next step|n\u00e4chste[rn]? schritt|n\u00e4chster schritt|nast\u0119pny krok|kolejny krok"


def handover_next_step(ws):
    """The 'next step' line from handover/LATEST.md, or None if the note has none yet."""
    note = Path(ws) / "handover/LATEST.md"
    if not note.is_file():
        return None
    lines = note.read_text(encoding="utf-8", errors="replace").splitlines()
    if any("<!-- handover:empty -->" in l or "No session has been handed over yet" in l for l in lines):
        return None
    for i, line in enumerate(lines):
        if re.search(NEXT_STEP, line, re.I):
            text = re.sub(r"^[\s*#-]*(\*\*)?[^:*]*?(" + NEXT_STEP + r")[^:*]*(\*\*)?\s*:?\s*(\*\*)?\s*", "",
                          line, flags=re.I).strip(" *")
            if not text:  # a heading or label: the step is the next line with text
                text = next((l.strip(" -*") for l in lines[i + 1:] if l.strip(" -*")), "")
            return text or None
    return None


def status(ws):
    """What needs the human's attention, in plain words. Read-only."""
    ws = Path(ws)
    read_manifest(ws)
    R = review_tool()
    try:
        prof = json.loads((ws / ".living/profile.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        prof = {}
    current = R.current_decisions(ws) if (ws / "decisions").is_dir() else []
    lines = [f"Workspace: {ws} (profile: {prof.get('profile', '?')}, language: {prof.get('language', '?')})",
             f"Rules in force: {len(current)} current decision(s). List them: python3 tools/review.py current"]
    todo = []
    for p in sorted((ws / "proposals").glob("*.md")) if (ws / "proposals").is_dir() else []:
        try:
            meta, _, body = R.split_frontmatter(p.read_text(encoding="utf-8"), p.name)
        except (R.Refusal, UnicodeDecodeError):
            todo.append(f"proposals/{p.name} cannot be read as a proposal; run doctor")
            continue
        if meta.get("status") in R.REVIEWABLE:
            title = re.search(r"^# Proposal: (.+)$", body, re.M)
            what = {"new": "new rule", "replace": "replaces a rule", "retire": "retires a rule"}.get(
                meta.get("kind"), "exception to a rule")
            todo.append(f"Review proposals/{p.name} ({what}): {title.group(1).strip() if title else 'no title'}")
            todo.append(f"    when you have decided, run in the workspace: python3 tools/review.py review "
                        f"proposals/{p.name} --outcome approve|reject|defer --by \"Your Name\"")
    kinbox = ws / "knowledge/inbox.md"
    if kinbox.is_file():
        n = kinbox.read_text(encoding="utf-8", errors="replace").count("---knowledge---")
        if n:
            todo.append(f"{n} knowledge suggestion(s) in knowledge/inbox.md to keep or delete")
    due = [rel for rel, days, problem in knowledge_ages(ws) if problem or (days is not None and days > STALE_DAYS)]
    if due:
        todo.append(f"{len(due)} knowledge file(s) due for a re-check, e.g. {due[0]}")
    try:
        counted = read_runs(ws)["work"]
    except Refusal as e:
        counted = {}
        todo.append(str(e))
    for n, e in sorted(counted.items()):
        if run_is_due(e):
            todo.append(f"'{n}' has come up {e['count']} times: decide whether to automate it, keep it manual or "
                        f"decide later (living.py runs . --decide {n} automate|manual|later)")
    inbox = ws / "lessons/inbox.md"
    if inbox.is_file():
        n = inbox.read_text(encoding="utf-8", errors="replace").count("---lesson---")
        if n:
            todo.append(f"{n} lesson suggestion(s) in lessons/inbox.md to approve or delete")
    for f in ("SYSTEM.md", "PRINCIPLES.md"):
        if (ws / f).is_file():
            try:
                approved = R.split_frontmatter((ws / f).read_text(encoding="utf-8"), f)[0].get("status") == "approved"
            except R.Refusal:
                approved = False
            if not approved:
                todo.append(f"Read {f} and change status: draft to status: approved when it is right")
    lines += ["Waiting for you:", *(f"  - {x}" for x in todo)] if todo else ["Waiting for you: nothing."]
    step = handover_next_step(ws)
    if step:
        lines.append(f"Last session's next step: {step}")
    health = doctor(ws)
    errors = sum(1 for lvl, _ in health if lvl == "ERROR")
    warns = sum(1 for lvl, _ in health if lvl == "WARN")
    lines.append(f"Health: {errors} error(s), {warns} warning(s)." + (" Details: living.py doctor" if errors or warns else ""))
    return "\n".join(lines)


SINCE_COVERED = ("decisions", "proposals", "knowledge", "lessons", "handover", "SYSTEM.md", "PRINCIPLES.md")
SINCE_SKIP = (".git", ".living", ".claude", ".codex", ".agents", "tools", "__pycache__")
SINCE_SHOWN = 15


def changed_files(ws, since, untouched=()):
    """Workspace files whose file date on this computer is on or after since, newest first.
    Files still exactly as Living System installed them are left out: nobody changed their content."""
    import datetime
    ws = Path(ws)
    out = []
    for top, dirs, files in os.walk(ws):
        rel_top = Path(top).relative_to(ws)
        dirs[:] = sorted(d for d in dirs if not (rel_top == Path(".") and d in SINCE_SKIP) and d != "__pycache__")
        for name in files:
            p = Path(top) / name
            if p.is_symlink() or name in (".gitkeep", ".review.lock"):
                continue
            day = datetime.date.fromtimestamp(p.stat().st_mtime)
            rel = p.relative_to(ws).as_posix()
            if day >= since and not (rel in untouched and sha256(p) == untouched[rel]):
                out.append((day.isoformat(), rel))
    return sorted(out, key=lambda r: (r[0], r[1]), reverse=True)


def since(ws, date, today=None):
    """What changed in the workspace on or after date, in plain words, rules first. Read-only."""
    import datetime
    ws = Path(ws)
    manifest = read_manifest(ws)
    untouched = dict(manifest["files"])
    for entry in manifest.get("modules", {}).values():
        untouched.update(entry["files"])
    R = review_tool()
    today = today or datetime.date.today()
    try:
        start = datetime.date.fromisoformat(date)
    except (TypeError, ValueError):
        raise Refusal(f"{date!r} is not a date like 2026-10-01") from None
    if start > today:
        raise Refusal(f"{date} is in the future; give the day you left")
    lines = [f"What changed since {start} ({(today - start).days} day(s) ago). Read-only: nothing was changed."]

    rules = []
    if (ws / "decisions").is_dir():
        decs = R.decisions(ws)
        titles = {k: title for k, title, *_ in R.history(ws)}
        for k, m in sorted(decs.items(), key=lambda kv: (kv[1].get("date", ""), kv[0])):
            if m.get("status") != "approved" or str(m.get("date", "")) < start.isoformat():
                continue
            by = f"approved by {m.get('approved_by', '?')} on {m.get('date')}"
            old = m.get("supersedes")
            if m.get("kind") == R.RETIREMENT:
                rules.append(f"Retired: {titles.get(old, old)} ({old}); no rule replaces it. {by}")
            elif old:
                how = "Amended" if "\n### Exception\n" in (ws / k).read_text(encoding="utf-8") else "Replaced"
                rules.append(f"{how}: {titles.get(old, old)}. Now read {k} ({titles[k]}). {by}")
            else:
                rules.append(f"New rule: {titles[k]} ({k}). {by}")
    files = changed_files(ws, start, untouched)
    for f in ("SYSTEM.md", "PRINCIPLES.md"):
        if f in (rel for _, rel in files):
            rules.append(f"{f} was edited (file date); read it again")
    lines += ["Rules (read these first):", *(f"  - {x}" for x in rules)] if rules else ["Rules: no changes."]

    props = []
    for p in sorted((ws / "proposals").glob("*.md")) if (ws / "proposals").is_dir() else []:
        try:
            meta, _, body = R.split_frontmatter(p.read_text(encoding="utf-8"), p.name)
        except (R.Refusal, UnicodeDecodeError):
            continue
        title = (re.search(r"^# Proposal: (.+)$", body, re.M) or re.match("(.*)", p.stem)).group(1).strip()
        reviewed, made = str(meta.get("reviewed_on", "")), str(meta.get("date", ""))
        if reviewed >= start.isoformat():
            outcome = {"promoted": "approved", "rejected": "rejected", "deferred": "deferred"}.get(
                meta.get("status"), meta.get("status"))
            props.append(f"{outcome} on {reviewed}: {title} (proposals/{p.name})")
        elif made >= start.isoformat() and meta.get("status") in R.REVIEWABLE:
            props.append(f"new, waits for review: {title} (proposals/{p.name})")
    lines += ["Proposals:", *(f"  - {x}" for x in props)] if props else ["Proposals: no changes."]

    other = []
    if "handover/LATEST.md" in (rel for _, rel in files):
        step = handover_next_step(ws)
        other.append("handover/LATEST.md was updated" + (f"; its next step: {step}" if step else ""))
    try:
        counted = read_runs(ws)["work"]
    except Refusal:
        counted = {}
    for name, e in sorted(counted.items()):
        if e["last"] >= start.isoformat():
            other.append(f"repeated work '{name}': {e['count']} run(s) in total, last on {e['last']}"
                         + (", now waits for your decision" if run_is_due(e) else ""))
    for area, label in (("knowledge/", "knowledge"), ("lessons/", "lessons")):
        hits = [rel for _, rel in files if rel.startswith(area)]
        if hits:
            other.append(f"{len(hits)} {label} file(s) changed, e.g. {hits[0]}")
    lines += ["Other changes:", *(f"  - {x}" for x in other)] if other else ["Other changes: none recorded."]

    rest = [(day, rel) for day, rel in files if rel.split("/", 1)[0] not in SINCE_COVERED]
    if rest:
        lines.append("Other files changed (file dates on this computer; a copy or git pull can change them):")
        lines += [f"  - {day}  {rel}" for day, rel in rest[:SINCE_SHOWN]]
        if len(rest) > SINCE_SHOWN:
            lines.append(f"  - and {len(rest) - SINCE_SHOWN} more")
    lines.append("Next: " + ("read the changed rules first; then run status for what waits for you." if rules else
                             "run status for what waits for you."))
    return "\n".join(lines)


def guard_tool():
    import importlib.util
    spec = importlib.util.spec_from_file_location("living_guard", HERE / "guard.py")
    mod = importlib.util.module_from_spec(spec)
    saved, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = saved
    return mod


# Text that talks to an AI instead of to a person: a sign that a document tries to steer the agent.
STEERING = re.compile(r"(?i)\b(?:"
    r"(?:ignore|disregard|forget|override)\s+(?:all\s+|any\s+|the\s+|your\s+)*(?:previous|prior|above|earlier|other)\s+"
    r"(?:instructions|rules|messages|prompts?)"
    r"|you\s+are\s+now\s+(?:a|an|in)\b|new\s+instructions\s*:|system\s+prompt\b|developer\s+mode\b"
    r"|do\s+not\s+(?:tell|inform|show)\s+(?:the\s+)?(?:user|human)|without\s+(?:asking|telling)\s+the\s+(?:user|human)"
    r"|(?:ai|assistant|agent)\s*:\s*(?:please\s+)?(?:run|approve|delete|send)"
    r"|approve\s+(?:this|the|all)\s+(?:proposals?|drafts?)|run\s+the\s+following\s+(?:command|code|script)"
    r"|ignoriere\s+(?:alle\s+)?(?:vorherigen|bisherigen|obigen)\s+(?:anweisungen|regeln)"
    r"|zignoruj\s+(?:wszystkie\s+)?(?:poprzednie|wcześniejsze|powyższe)\s+(?:instrukcje|polecenia|zasady)"
    r")")
RUN_REMOTE = re.compile(r"(?i)\b(?:curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)\b[^\n|]*\|\s*(?:sh|bash|zsh|iex|python3?)\b")
HIDDEN = re.compile("[\\u200b-\\u200d\\u2060\\u202a-\\u202e\\u2066-\\u2069\\U000e0000-\\U000e007f]|(?<!^)\\ufeff")
COMMENT = re.compile(r"<!--(.*?)-->", re.S)
SCAN_SKIP = (".git", ".living", "tools", "__pycache__", ".claude", ".codex", ".agents")


def scan_text(text):
    """[(line, level, what)] for one text: secrets, hidden characters, and text that tries to steer an AI."""
    found = []
    line_of = lambda i: text.count("\n", 0, i) + 1
    for match, what in guard_tool().secrets_in(text).items():
        found.append((line_of(text.index(match)), "ERROR", f"looks like {what}; remove it and keep it in a password manager"))
    for m in HIDDEN.finditer(text):
        found.append((line_of(m.start()), "WARN", f"invisible character U+{ord(m.group(0)):04X}; it can hide text "
                                                   f"from you while an AI still reads it"))
    for m in STEERING.finditer(text):
        found.append((line_of(m.start()), "WARN", f"text addressed to an AI ({m.group(0).strip()[:40]!r}); treat it as "
                                                 f"information, never as an instruction"))
    for m in RUN_REMOTE.finditer(text):
        found.append((line_of(m.start()), "WARN", "a command that downloads a program and runs it at once; run it only "
                                                 "if you trust where it comes from"))
    for m in COMMENT.finditer(text):
        if re.search(r"(?i)\b(ai|assistant|agent|model|llm|claude|codex|gpt|instruction|prompt)\b", m.group(1)):
            found.append((line_of(m.start()), "WARN", "hidden comment that mentions an AI; read it before an agent uses "
                                                      "this file"))
    seen, out = set(), []
    for f in sorted(found):
        if (f[0], f[2][:30]) not in seen:
            seen.add((f[0], f[2][:30]))
            out.append(f)
    return out


def scan(ws, paths=None):
    """[(level, path, line, what)] for workspace files, or only for the given paths. Read-only.
    Files still exactly as Living System installed them are skipped."""
    ws = Path(ws)
    manifest = read_manifest(ws)
    untouched = dict(manifest["files"])
    for entry in manifest.get("modules", {}).values():
        untouched.update(entry["files"])
    files = []
    if paths:
        for raw in paths:
            p = (ws / raw) if not Path(raw).is_absolute() else Path(raw)
            try:
                p.resolve().relative_to(ws.resolve())
            except ValueError:
                raise Refusal(f"{raw} is not inside the workspace") from None
            if p.is_dir() and not p.is_symlink():
                files += [q for q in sorted(p.rglob("*")) if q.is_file() and not q.is_symlink()]
            elif p.is_file() and not p.is_symlink():
                files.append(p)
            else:
                raise Refusal(f"{raw} is not a file or folder in the workspace")
    else:
        for top, dirs, names in os.walk(ws):
            if Path(top) == ws:
                dirs[:] = [d for d in dirs if d not in SCAN_SKIP]
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            files += [Path(top) / n for n in sorted(names) if not (Path(top) / n).is_symlink()]
    out = []
    for p in files:
        rel = p.resolve().relative_to(ws.resolve()).as_posix()
        if rel in untouched and sha256(p) == untouched[rel]:
            continue
        data = p.read_bytes()
        if b"\0" in data[:4096]:
            continue  # not a text file
        for line, level, what in scan_text(data.decode("utf-8", errors="replace")):
            out.append((level, rel, line, what))
    return out


def format_scan(results):
    if not results:
        return "Nothing found: no secrets, hidden characters or text addressed to an AI."
    lines = [f"{lvl}: {path}, line {line}: {what}" for lvl, path, line, what in results]
    return "\n".join(lines + [f"{sum(r[0] == 'ERROR' for r in results)} secret(s), "
                              f"{sum(r[0] == 'WARN' for r in results)} warning(s). Nothing was changed."])


HANDBOOK_MARK ="<!-- living-system handbook: a generated copy, not the rules -->"


def handbook(ws, today=None):
    """A readable copy of the rules in force, waiting proposals, workflows and the manual steps. Read-only."""
    import datetime
    ws = Path(ws)
    read_manifest(ws)
    R = review_tool()
    today = today or datetime.date.today()
    out = [HANDBOOK_MARK, f"# Working without AI: {ws.resolve().name}", "",
           f"Made on {today} with `living.py handbook`. This is a copy for reading, not the rules. If it differs "
           f"from the files in `decisions/`, the files win. Make it again after a rule changes.", ""]
    decs = R.decisions(ws) if (ws / "decisions").is_dir() else {}
    current = R.current_decisions(ws) if decs else []
    out += [f"## The rules in force ({len(current)})", ""]
    for k in sorted(current, key=lambda k: (decs[k].get("date", ""), k)):
        body = R.split_frontmatter((ws / k).read_text(encoding="utf-8"), k)[2]
        title = (re.search(r"^# (.+)$", body, re.M) or re.match("(.*)", Path(k).stem)).group(1).strip()
        try:
            rule = R.section(body, "Rule", k)
        except R.Refusal:
            rule = "(no Rule section; read the file)"
        out += [f"### {title}", "", rule, "",
                f"Approved by {decs[k].get('approved_by', '?')} on {decs[k].get('date', '?')}. File: `{k}`", ""]
    if not current:
        out += ["No approved rules yet. Until there are, nothing here is a rule.", ""]
    for f in ("SYSTEM.md", "PRINCIPLES.md"):
        if (ws / f).is_file():
            try:
                approved = R.split_frontmatter((ws / f).read_text(encoding="utf-8"), f)[0].get("status") == "approved"
            except R.Refusal:
                approved = False
            out.append(f"- `{f}`: {'approved, so it counts as your rules' if approved else 'a draft, not a rule yet'}.")
    out.append("")
    waiting = []
    for p in sorted((ws / "proposals").glob("*.md")) if (ws / "proposals").is_dir() else []:
        try:
            meta, _, body = R.split_frontmatter(p.read_text(encoding="utf-8"), p.name)
        except (R.Refusal, UnicodeDecodeError):
            continue
        if meta.get("status") in R.REVIEWABLE:
            title = (re.search(r"^# Proposal: (.+)$", body, re.M) or re.match("(.*)", p.stem)).group(1).strip()
            waiting.append(f"- {title} (`proposals/{p.name}`): not a rule until someone approves it.")
    out += ["## Waiting for a decision", "", *(waiting or ["Nothing."]), ""]
    flows = []
    for d in sorted((ws / "workflows").iterdir()) if (ws / "workflows").is_dir() else []:
        ctx = d / "CONTEXT.md"
        if d.is_dir() and not d.is_symlink() and ctx.is_file():
            stages = [s.name for s in sorted(d.iterdir()) if s.is_dir() and re.match(r"\d\d-", s.name)]
            first = re.search(r"^# (.+)$", ctx.read_text(encoding="utf-8", errors="replace"), re.M)
            flows.append(f"- **{first.group(1).strip() if first else d.name}**: "
                         + (" → ".join(stages) if stages else "no stages") + f". Steps: `workflows/{d.name}/CONTEXT.md`")
    try:
        counted = read_runs(ws)["work"]
    except Refusal:
        counted = {}
    flows += [f"- '{n}' (counted {e['count']} times; your choice: {e.get('decision') or 'not decided'})"
              for n, e in sorted(counted.items())]
    out += ["## Your repeated work", "", *(flows or ["Nothing recorded yet."]), ""]
    step = handover_next_step(ws)
    if step:
        out += ["## Where the last session stopped", "", step, ""]
    out += ["## Doing it by hand", "",
            "- **Which rule applies?** The newest file in `decisions/` about it that no other approved decision "
            "names in `supersedes:`. The list above shows them.",
            "- **Changing a rule:** write a proposal in `proposals/` (the format is in `AGENTS.md` section 6). The "
            "person who may approve reviews it with `python3 tools/review.py review proposals/<file> "
            "--outcome approve|reject|defer --by \"Name\"`.",
            "- **Without Python:** the person who may approve writes a new file in `decisions/` with `status: "
            "approved`, today's `date`, and `supersedes:` naming the old file. Never edit or delete the old file. "
            "`review.py verify` will list it as written by hand, which is expected.",
            "- **Repeated work:** each workflow's `CONTEXT.md` lists its steps in plain words; do them in order and "
            "check the result yourself at each stop.",
            "- **Skills you want to keep:** `me/goals.md`, if your profile has it.", ""]
    return "\n".join(out)


def write_handbook(ws, target, text):
    """Save the handbook outside the workspace. Only a previous handbook is ever replaced."""
    ws, target = Path(ws).resolve(), Path(target).expanduser().resolve()
    if target.suffix.lower() not in (".md", ".txt"):
        raise Refusal("the handbook file name must end in .md or .txt")
    if ws in (target, *target.parents):
        raise Refusal("save the handbook outside the workspace, so no agent mistakes the copy for the rules")
    if not target.parent.is_dir():
        raise Refusal(f"folder {target.parent} does not exist")
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise Refusal(f"{target} is not a plain file; choose a new file name")
    if target.exists():
        with open(target, encoding="utf-8", errors="replace") as f:
            if f.readline().strip() != HANDBOOK_MARK:
                raise Refusal(f"{target} already exists and is not a handbook; choose a new file name")
    fd, tmp = tempfile.mkstemp(prefix=".living-handbook-", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
        os.replace(tmp, target)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return target


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
    i.add_argument("--coach", action="store_true", help="the agent also helps you keep and build your own skills")
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
    u = sub.add_parser("upgrade", help="plan (or with --apply, apply) updates from this Living System version")
    u.add_argument("workspace")
    u.add_argument("--apply", action="store_true")
    w = sub.add_parser("new-workflow", help="plan (or with --apply, create) a staged workflow folder")
    w.add_argument("workspace")
    w.add_argument("name")
    w.add_argument("--stages", required=True, help="comma-separated stage names in order, e.g. research,draft,review")
    w.add_argument("--goal", default="")
    w.add_argument("--apply", action="store_true")
    pt = sub.add_parser("protect", help="put back a missing write guard or hook file (plan unless --apply)")
    pt.add_argument("workspace")
    pt.add_argument("--apply", action="store_true")
    ex = sub.add_parser("export", help="pack the workspace into one zip file (plan unless --apply)")
    ex.add_argument("workspace")
    ex.add_argument("file", help="the .zip file to create, outside the workspace")
    ex.add_argument("--apply", action="store_true")
    rn = sub.add_parser("runs", help="Third-Run Rule: count a kind of work, record a decision, or list counts")
    rn.add_argument("workspace")
    g = rn.add_mutually_exclusive_group()
    g.add_argument("--add", metavar="NAME", help="count one more run of this kind of work")
    g.add_argument("--decide", nargs=2, metavar=("NAME", "DECISION"), help="automate, manual or later")
    g.add_argument("--forget", metavar="NAME", help="delete this entry")
    rn.add_argument("--after", type=int, help="with --decide NAME later: ask again after this many more runs")
    pr = sub.add_parser("propose", help="plan (or with --apply, write) a proposal; never approves anything")
    pr.add_argument("workspace")
    pr.add_argument("--kind", required=True, choices=PROPOSE_KINDS)
    pr.add_argument("--title", required=True)
    pr.add_argument("--rule", required=True, help="the proposed rule; for retire, why it no longer applies")
    pr.add_argument("--evidence", required=True, help="what this comes from, e.g. 'setup answer, 2026-10-24'")
    pr.add_argument("--why", default="")
    pr.add_argument("--by", default="agent")
    pr.add_argument("--target", help="for exception, replace and retire: the current decision it changes")
    pr.add_argument("--apply", action="store_true")
    d = sub.add_parser("doctor", help="read-only health check of a workspace")
    d.add_argument("workspace")
    s = sub.add_parser("status", help="what needs your attention, in plain words (read-only)")
    s.add_argument("workspace")
    sn = sub.add_parser("since", help="what changed while you were away, rules first (read-only)")
    sn.add_argument("workspace")
    when = sn.add_mutually_exclusive_group(required=True)
    when.add_argument("--date", help="the day you left, e.g. 2026-10-01")
    when.add_argument("--days", type=int, help="or: how many days you were away")
    sc = sub.add_parser("scan", help="look for secrets and hidden instructions in workspace files (read-only)")
    sc.add_argument("workspace")
    sc.add_argument("paths", nargs="*", help="only these files or folders, e.g. incoming")
    hb = sub.add_parser("handbook", help="a readable copy of your rules and workflows, for working without AI")
    hb.add_argument("workspace")
    hb.add_argument("--out", help="save it to this .md file outside the workspace (default: print it)")
    a = ap.parse_args(argv)
    for name in ("workspace", "dir"):  # PowerShell passes ~ through unexpanded
        if getattr(a, name, None):
            setattr(a, name, os.path.expanduser(getattr(a, name)))
    try:
        if a.cmd == "init":
            ws = init(a.dir, a.profile, a.language, a.calm_replies, a.coach)
            print(f"Created workspace: {ws.resolve()}")
            print(f"Profile: {a.profile} | language: {a.language} | calm replies: {'on' if a.calm_replies else 'off'} | coach: {'on' if a.coach else 'off'}")
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
        elif a.cmd == "upgrade":
            plan = upgrade(a.workspace, a.apply)
            print(format_upgrade_plan(plan))
            if any(act not in ("same",) for act, *_ in plan):
                print("Upgraded." if a.apply else "Nothing was written. Run again with --apply to upgrade.")
        elif a.cmd == "protect":
            missing = protect(a.workspace, a.apply)
            print("Nothing is missing: the guard and both hook files are in place." if not missing else
                  ("Put back: " if a.apply else "Would put back: ") + ", ".join(missing) +
                  ("" if a.apply else ". Nothing was written. Run again with --apply."))
        elif a.cmd == "export":
            files = export(a.workspace, os.path.expanduser(a.file), a.apply)
            print(f"{len(files)} files" + (f" saved to {Path(a.file).expanduser().resolve()}." if a.apply else
                  ". Nothing was written. Run again with --apply to create the zip file."))
        elif a.cmd == "runs":
            name, decision = (a.decide or (None, None))
            work, message = runs(a.workspace, add=a.add, decide=name, decision=decision, after=a.after, forget=a.forget)
            print(message or format_runs(work))
        elif a.cmd == "propose":
            rel, text = propose(a.workspace, a.kind, a.title, a.rule, a.evidence, a.why, a.by, a.target, apply=a.apply)
            print(text)
            print(f"Written {rel}. It is not a rule yet. Read it; when you have decided, run in the workspace:\n"
                  f"  python3 tools/review.py review {rel} --outcome approve|reject|defer --by \"Your Name\""
                  if a.apply else f"Nothing was written. Run again with --apply to create {rel}.")
        elif a.cmd == "status":
            print(status(a.workspace))
        elif a.cmd == "since":
            import datetime
            if a.days is not None and a.days < 0:
                raise Refusal("--days must be 0 or more")
            date = a.date or (datetime.date.today() - datetime.timedelta(days=a.days)).isoformat()
            print(since(a.workspace, date))
        elif a.cmd == "scan":
            results = scan(a.workspace, a.paths)
            print(format_scan(results))
            return 1 if any(lvl == "ERROR" for lvl, *_ in results) else 0
        elif a.cmd == "handbook":
            text = handbook(a.workspace)
            if a.out:
                print(f"Saved {write_handbook(a.workspace, os.path.expanduser(a.out), text)}. It is a copy, not the rules.")
            else:
                print(text)
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

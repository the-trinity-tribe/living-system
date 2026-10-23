#!/usr/bin/env python3
"""Create and inspect a Living System workspace. Standard library only.

  living.py init <dir> --profile <p> --language <code> [--calm-replies]
  living.py value-score <workspace>

`init` writes into a NEW folder, built in a temporary folder next to it and renamed
at the end, so a failure never leaves a half-made workspace.
"""
import argparse
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
        text, add = base.read_text(), p.read_text()
        text = text.replace(MARKER, add.rstrip("\n") + "\n" + MARKER, 1) if MARKER in text else text.rstrip("\n") + "\n" + add
        base.write_text(text)


def strip_markers(dst):
    for p in dst.rglob("*.md"):
        t = p.read_text()
        if MARKER in t:
            p.write_text(t.replace(MARKER + "\n", "").replace(MARKER, ""))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_manifest(ws):
    files = {str(p.relative_to(ws)): sha256(p)
             for p in sorted(ws.rglob("*")) if p.is_file() and p.name != "manifest.json"}
    (ws / ".living" / "manifest.json").write_text(
        json.dumps({"kernel_version": KERNEL_VERSION, "files": files}, indent=2) + "\n")


def build(ws, profile, language, calm_replies):
    copy_tree(CORE / "template", ws)
    copy_tree(CORE / "profiles" / profile, ws)
    apply_appends(CORE / "profiles" / profile, ws)
    strip_markers(ws)
    (ws / "tools").mkdir()
    shutil.copyfile(HERE / "review.py", ws / "tools" / "review.py")
    (ws / ".living").mkdir()
    (ws / ".living" / "profile.json").write_text(json.dumps(
        {"profile": profile, "language": language, "calm_replies": bool(calm_replies)}, indent=2) + "\n")
    write_manifest(ws)


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
        os.rename(tmp, target)  # replaces an empty folder; atomic on one filesystem
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
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
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
    return counts, unscored


def format_score(counts, unscored):
    head = f"{'':8}" + "".join(f"{s:>11}" for s in SCORES)
    rows = [f"{w:<8}" + "".join(f"{counts[w][s]:>11}" for s in SCORES) for w in ("before", "after")]
    notes = [f"{w}: {n} not scored yet" for w, n in unscored.items() if n]
    return "\n".join([head, *rows, *notes])


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
    a = ap.parse_args(argv)
    try:
        if a.cmd == "init":
            ws = init(a.dir, a.profile, a.language, a.calm_replies)
            print(f"Created workspace: {ws.resolve()}")
            print(f"Profile: {a.profile} | language: {a.language} | calm replies: {'on' if a.calm_replies else 'off'}")
            print("Undo: delete that folder. Next: open it in Claude Code or Codex.")
        else:
            print(format_score(*value_score(a.workspace)))
    except Refusal as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

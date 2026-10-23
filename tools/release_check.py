#!/usr/bin/env python3
"""Pre-release safety scan for the Living System repository. Standard library only. Read-only.

    python3 tools/release_check.py            # scan the files git tracks (or all files if git is missing)

ERROR (exit 1): private names, personal paths, e-mail addresses, things that look like secrets,
demo names inside product templates or modules, AI co-author trailers in commit messages.
WARN (exit 0): wording that may overclaim (for example "secure" or "compliant") on a line that
does not also say what is *not* promised. A person reads the warnings; the script does not decide.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

# Patterns are assembled from parts so this file does not match itself.
PRIVATE = [re.compile(p, re.I) for p in (
    "TTT" + r"[- ]System", r"/home/[a-z_][a-z0-9_-]*/", r"[A-Z]:\\\\Users\\\\", r"/Users/[A-Za-z0-9_-]+/",
)]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMAIL_OK = re.compile(r"@(example\.(com|org|net)|users\.noreply\.github\.com)$", re.I)
SECRET = [re.compile(p) for p in (
    r"\bsk-[A-Za-z0-9_-]{20,}", r"\bgh[pousr]_[A-Za-z0-9]{30,}", r"\bAKIA[0-9A-Z]{16}\b",
    r"-----BEGIN [A-Z ]*PRIVATE " + "KEY-----", r"\bxox[abpr]-[A-Za-z0-9-]{10,}",
    r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
)]
DEMO_NAMES = re.compile(r"\b(Moss & Circuit|Moss and Circuit|Riverside|Maya Chen|Leo Martin|Sam Okafor)\b")
OVERCLAIM = re.compile(r"(?i)\b(production[- ]ready|enterprise[- ]grade|secure|compliant|guarantee[sd]?|"
                       r"bank[- ]grade|military[- ]grade|unhackable)\b")
NEGATION = re.compile(r"(?i)\b(not|no|never|without|nothing|cannot|isn't|doesn't|does not|is not)\b")
TRAILER = re.compile(r"(?im)^\s*Co-Authored-By:.*\b(claude|anthropic|openai|chatgpt|codex|copilot|gpt)\b")
TEXT_SUFFIXES = {".md", ".py", ".json", ".html", ".txt", ".cff", ".yml", ".yaml", ".toml", ".cfg", ""}


def tracked_files(root):
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True)
        return [root / p for p in out.stdout.decode("utf-8").split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts]


def scan(root, files=None, commit_messages=None):
    """Return (level, location, message) findings for the given files."""
    root = Path(root)
    findings = []
    for p in files if files is not None else tracked_files(root):
        if p.resolve() == SELF or not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        is_test = rel.startswith("tests/")
        for n, line in enumerate(text.splitlines(), 1):
            where = f"{rel}:{n}"
            for pat in PRIVATE:
                if pat.search(line):
                    findings.append(("ERROR", where, "private name or personal path"))
            for m in EMAIL.finditer(line):
                if not EMAIL_OK.search(m.group(0)):
                    findings.append(("ERROR", where, f"e-mail address {m.group(0)!r}"))
            if not is_test:
                for pat in SECRET:
                    if pat.search(line):
                        findings.append(("ERROR", where, "looks like a secret or key"))
            if rel.startswith(("core/", "modules/")) and DEMO_NAMES.search(line):
                findings.append(("ERROR", where, "demo name inside a product template or module"))
            if p.suffix.lower() in (".md", ".html") and OVERCLAIM.search(line) and not NEGATION.search(line):
                findings.append(("WARN", where, f"check the claim: {OVERCLAIM.search(line).group(0)!r}"))
    for sha, message in commit_messages if commit_messages is not None else git_messages(root):
        if TRAILER.search(message):
            findings.append(("ERROR", f"commit {sha[:8]}", "AI co-author trailer in the commit message"))
    return findings


def git_messages(root):
    try:
        out = subprocess.run(["git", "-C", str(root), "log", "--format=%H%x00%B%x01"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return []
    return [tuple(c.strip("\n").split("\0", 1)) for c in out.stdout.decode("utf-8", "replace").split("\1")
            if "\0" in c]


def main():
    findings = scan(ROOT)
    for level, where, msg in sorted(findings, key=lambda f: (f[0] != "ERROR", f[1])):
        print(f"{level}: {where}: {msg}")
    errors = sum(1 for f in findings if f[0] == "ERROR")
    warns = len(findings) - errors
    print(f"{errors} error(s), {warns} warning(s)." if findings else "Release check: nothing found.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

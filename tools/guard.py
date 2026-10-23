#!/usr/bin/env python3
"""Write guard for a Living System workspace. Standard library only.

Claude Code and Codex run this before an agent changes a file (see .claude/settings.json and
.codex/hooks.json in the workspace). It reads the tool call as JSON on stdin and exits with 2,
explaining why on stderr, when the change would:

- write, move or delete anything in decisions/ (only `tools/review.py review` creates decisions);
- mark SYSTEM.md or PRINCIPLES.md as `status: approved` (only the human approves them);
- set a proposal's outcome by hand (`status: promoted|rejected|deferred` is written by review.py);
- change the guard or its hook settings, or the review tool.

Anything else exits 0, and the agent's normal permission prompts apply. This is a guard rail, not a
security boundary: shell commands are checked by simple patterns only, and a person (or an agent
outside these tools) can still change any file.
"""
import json
import re
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
GUARDED = ("tools/guard.py", "tools/review.py", ".claude/settings.json", ".codex/hooks.json")
APPROVAL_FILES = ("SYSTEM.md", "PRINCIPLES.md")
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
SHELL_TOOLS = ("Bash", "shell", "local_shell", "exec_command")
CHANGE_VERBS = re.compile(r"\b(rm|mv|tee|truncate|unlink|del|rmdir|Remove-Item|Set-Content|Add-Content|Out-File|"
                          r"Move-Item|Rename-Item|Clear-Content)\b|\bsed\s+(-\w*\s+)*-i|\bperl\s+-\w*i|write_text|"
                          r"write_bytes|open\([^)]*['\"][wax]")
COPY_VERBS = re.compile(r"\b(cp|Copy-Item|install|rsync)\b")
HARMLESS_REDIRECT = re.compile(r"\d?>&\d|\d?>>?\s*(/dev/null|\$null|NUL)\b")


def rel(path, cwd):
    """The path relative to the workspace, with /, or None when it is outside the workspace."""
    p = Path(str(path).replace("\\", "/"))  # PowerShell and cmd write decisions\\x.md
    if not p.is_absolute():
        p = Path(cwd or WS) / p
    try:
        return p.resolve().relative_to(WS).as_posix()
    except (ValueError, OSError):
        return None


def status_of(text):
    m = re.match(r"---\r?\n(.*?)\r?\n---", text or "", re.S)
    s = re.search(r"^status:\s*(\S+)", m.group(1), re.M) if m else None
    return s.group(1) if s else None


def problem(path, new_text=None, deleting=False):
    """Why this change to a workspace path is not allowed, or None."""
    if path is None:
        return None
    if path == "decisions" or path.startswith("decisions/"):
        return ("decisions are created only by `python3 tools/review.py review` after a human decides, and are "
                "never edited or deleted. Write a proposal instead (AGENTS.md section 6)")
    if path in GUARDED:
        return "this file keeps the review rules and this guard working; only the human changes it"
    if new_text is None or deleting:
        return None
    if path in APPROVAL_FILES and status_of(new_text) == "approved" and status_of(current(path)) != "approved":
        return f"only the human marks {path} as approved; tell them what to check and let them change the status line"
    if path.startswith("proposals/") and status_of(new_text) in ("promoted", "rejected", "deferred") \
            and status_of(new_text) != status_of(current(path)):
        return ("a proposal's outcome is recorded only by `python3 tools/review.py review` when the human has "
                "decided (AGENTS.md section 7)")
    return None


def current(path):
    try:
        return (WS / path).read_text(encoding="utf-8")
    except OSError:
        return ""


def after_edit(path, tool_input):
    """The file text after a Claude Code Edit, MultiEdit or Write."""
    if "content" in tool_input:
        return tool_input["content"]
    text = current(path)
    for e in tool_input.get("edits") or [tool_input]:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def patch_changes(patch):
    """(path, added lines, deleting) for each file a Codex apply_patch text touches. A move counts as
    deleting the old path and adding the new one."""
    out = []
    for line in patch.splitlines():
        m = re.match(r"\*\*\* (Add|Update|Delete) File: (.+)", line)
        if m:
            out.append([m.group(2).strip(), [], m.group(1) == "Delete"])
            continue
        mv = re.match(r"\*\*\* Move to: (.+)", line)
        if mv and out:
            out[-1][2] = True
            out.append([mv.group(1).strip(), out[-1][1], False])
        elif out and line.startswith("+"):
            out[-1][1].append(line[1:])
    return [(path, "\n".join(added), deleting) for path, added, deleting in out]


def shell_problem(cmd, cwd):
    """Best-effort check of a shell command: redirects, deleting or moving commands, and copies into a protected
    path, following `cd` steps. Reading protected files and running tools/review.py are always fine."""
    clean = HARMLESS_REDIRECT.sub("", cmd)
    if re.search(r"write_text|write_bytes|open\(", clean):  # inline Python writes
        for name in ("decisions/",) + GUARDED:
            if name in clean:
                return problem(name if name != "decisions/" else "decisions")
    here = Path(cwd or WS)
    for part in re.split(r"&&|\|\||;|\|", clean):
        words = part.split()
        if not words:
            continue
        if words[0] in ("cd", "Set-Location", "pushd") and len(words) > 1:
            here = here / words[1].strip("'\"")
            continue
        targets = re.findall(r">>?\s*['\"]?([^\s'\";|&<>]+)", part)
        if CHANGE_VERBS.search(part):
            targets += words[1:]
        elif COPY_VERBS.search(words[0]) and len(words) > 2:
            targets.append(words[-1])
        for target in targets:
            path = rel(target.strip("'\""), here)
            if path and (path == "decisions" or path.startswith("decisions/") or path in GUARDED):
                return problem(path)
    return None


def check(event):
    tool = event.get("tool_name", "")
    data = event.get("tool_input") or {}
    cwd = event.get("cwd")
    if tool in EDIT_TOOLS:
        path = rel(data.get("file_path") or data.get("notebook_path") or "", cwd)
        return problem(path, after_edit(path, data) if path else None)
    if tool == "apply_patch" or (tool in SHELL_TOOLS and "*** Begin Patch" in str(data.get("command", ""))):
        cmd = data.get("command") or data.get("patch") or data.get("input") or ""
        cmd = cmd if isinstance(cmd, str) else "\n".join(cmd)
        for path, added, deleting in patch_changes(cmd):
            status = re.search(r"^status:\s*\S+", added, re.M)
            why = problem(rel(path, cwd), f"---\n{status.group(0)}\n---" if status else None, deleting)
            if why:
                return why
        return None
    if tool in SHELL_TOOLS:
        cmd = data.get("command", "")
        return shell_problem(cmd if isinstance(cmd, str) else " ".join(cmd), cwd)
    return None


def main():
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0  # not a tool call we understand: leave it to the normal permission prompts
    why = check(event)
    if why:
        print(f"Living System guard: blocked. {why}.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

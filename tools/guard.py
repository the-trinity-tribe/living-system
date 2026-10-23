#!/usr/bin/env python3
"""Write guard for a Living System workspace. Standard library only.

Claude Code and Codex run this before an agent changes a file (see .claude/settings.json and
.codex/hooks.json in the workspace). It reads the tool call as JSON on stdin and exits with 2,
explaining why on stderr, when the change would:

- write, move or delete anything in decisions/ (only `tools/review.py review` creates decisions);
- mark SYSTEM.md or PRINCIPLES.md as `status: approved` (only the human approves them);
- set a proposal's outcome by hand (`status: promoted|rejected|deferred` is written by review.py);
- change or remove the guard, its hook settings or the review tool (or a folder that holds them).

Anything else exits 0, and the agent's normal permission prompts apply. This is a guard rail, not a
security boundary: shell commands are read the way a shell would split them, but a script file or an
unusual command can still change files, and a person can always change any file.
"""
import json
import os
import re
import shlex
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
GUARDED = ("tools/guard.py", "tools/review.py", ".claude/settings.json", ".codex/hooks.json")
APPROVAL_FILES = ("SYSTEM.md", "PRINCIPLES.md")
OUTCOMES = ("promoted", "rejected", "deferred")
STATUS_WORDS = re.compile(r"\b(approved|promoted|rejected|deferred)\b")
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
SHELL_TOOLS = ("Bash", "shell", "local_shell", "exec_command")
# Commands whose file operands may be changed. Copy-like commands change only their destination.
CHANGING = {"rm", "rmdir", "unlink", "shred", "truncate", "tee", "mv", "ln", "touch", "chmod", "chown", "del",
            "erase", "rd", "remove-item", "set-content", "add-content", "clear-content", "out-file",
            "move-item", "rename-item", "new-item"}
REMOVING = CHANGING - {"tee", "touch", "set-content", "add-content", "out-file", "new-item", "chmod", "chown"}
COPYING = {"cp", "install", "rsync", "copy-item", "copy", "xcopy", "robocopy"}
IN_PLACE = {"sed", "perl", "ruby"}  # with -i
INTERPRETERS = {"python", "python3", "py", "node", "perl", "ruby", "php", "deno", "bun"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "pwsh", "powershell", "cmd"}
WRAPPERS = {"sudo", "env", "nice", "nohup", "time", "command", "exec", "xargs", "doas", "rtk", "proxy"}
WRITE_API = re.compile(r"""open\s*\([^,)]*,\s*['"][^'"]*[wax+][^'"]*['"]|mode\s*=\s*['"][^'"]*[wax+]|write_text|"""
                       r"""write_bytes|\.write\(|os\.(remove|unlink|rename|replace|rmdir|removedirs|truncate|chmod)|"""
                       r"""unlink\(|rmtree|shutil\.(move|copy\w*)|\.(rename|replace|touch|rmdir)\(|writeFile|"""
                       r"""appendFile|rmSync|unlinkSync|renameSync|Set-Content|Add-Content|Out-File|Remove-Item|"""
                       r"""Move-Item""")
REDIRECTS = {">", ">>", "1>", "1>>", ">|", "&>", "&>>"}
DECISIONS_MSG = ("decisions are created only by `python3 tools/review.py review` after a human decides, and are never "
                 "edited or deleted. Write a proposal instead (AGENTS.md section 6)")
GUARD_MSG = "this keeps the review rules and this guard working; only the human changes it"
STATUS_MSG = "only the human approves drafts, and only `python3 tools/review.py review` records a proposal's outcome"


class Blocked(Exception):
    pass


def rel(path, cwd):
    """Workspace-relative paths (with /) this path names: as written, and after following links."""
    p = Path(str(path).replace("\\", "/"))
    base = Path(cwd) if cwd else WS
    if not p.is_absolute():
        p = base / p
    out = set()
    try:
        resolved = p.resolve()
    except (OSError, RuntimeError):
        resolved = None
    for candidate in (Path(os.path.normpath(p)), resolved):
        try:
            out.add(candidate.relative_to(WS).as_posix())
        except (ValueError, TypeError, AttributeError):
            pass
    return out


def protected_reason(path, removing=False):
    """Why the agent may not touch this workspace path at all, or None."""
    if path in ("", "."):
        return GUARD_MSG if removing else None
    if path == "decisions" or path.startswith("decisions/"):
        return DECISIONS_MSG
    if path in GUARDED:
        return GUARD_MSG
    if removing and (any(g.startswith(path + "/") for g in GUARDED) or "decisions".startswith(path + "/")):
        return GUARD_MSG  # a folder that holds the guard, the review tool or the hook settings
    return None


def status_of(text):
    m = re.match(r"﻿?---\r?\n(.*?)\r?\n---", text or "", re.S)
    s = re.search(r"^status:\s*(\S+)", m.group(1), re.M) if m else None
    return s.group(1) if s else None


def current(path):
    try:
        return (WS / path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def status_sensitive(paths):
    return any(p in APPROVAL_FILES or p.startswith("proposals/") for p in paths)


def check_change(paths, new_text=None, removing=False):
    """Raise Blocked if writing new_text (None = content unknown) to these paths is not allowed."""
    for path in paths:
        why = protected_reason(path, removing)
        if why:
            raise Blocked(why)
        if new_text is None or removing:
            continue
        new, old = status_of(new_text), status_of(current(path))
        if path in APPROVAL_FILES and new == "approved" and old != "approved":
            raise Blocked(f"only the human marks {path} as approved; tell them what to check and let them change the "
                          f"status line")
        if path.startswith("proposals/") and new in OUTCOMES and new != old:
            raise Blocked(STATUS_MSG + " (AGENTS.md section 7)")


# ---------- Claude Code file tools ----------

def after_edit(path, tool_input):
    if "content" in tool_input:
        return tool_input["content"]
    text = current(path)
    for e in tool_input.get("edits") or [tool_input]:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


# ---------- Codex patches ----------

def apply_hunks(text, lines):
    """Apply apply_patch hunk lines to text. Returns the new text, or None when a hunk does not fit."""
    hunks = []
    for line in lines:
        if line.startswith("@@") or not hunks:
            hunks.append(([], []))
            if line.startswith("@@"):
                continue
        old, new = hunks[-1]
        if line.startswith(("-", " ")) or line == "":
            old.append(line[1:])
        if line.startswith(("+", " ")) or line == "":
            new.append(line[1:])
    for old, new in hunks:
        old_block, new_block = "\n".join(old), "\n".join(new)
        if old_block and old_block not in text:
            return None
        text = text.replace(old_block, new_block, 1) if old_block else text + new_block
    return text


def check_patch(patch, cwd):
    files = []  # [kind, path, body lines, move_to]
    for line in patch.splitlines():
        m = re.match(r"\*\*\* (Add|Update|Delete) File: (.+)", line)
        mv = re.match(r"\*\*\* Move to: (.+)", line)
        if m:
            files.append([m.group(1), m.group(2).strip(), [], None])
        elif mv and files:
            files[-1][3] = mv.group(1).strip()
        elif files and not line.startswith("*** "):
            files[-1][2].append(line)
    for kind, path, body, move_to in files:
        src = rel(path, cwd)
        if kind == "Delete":
            check_change(src, removing=True)
            continue
        if kind == "Add":
            text = "\n".join(l[1:] for l in body if l.startswith("+"))
        else:
            text = apply_hunks(next((current(p) for p in sorted(src)), ""), body)
        dest = rel(move_to, cwd) if move_to else src
        if move_to:
            check_change(src, removing=True)
        if text is None and status_sensitive(dest) and any(re.match(r"[+-]status:", l) for l in body):
            raise Blocked("this patch changes a status line the guard cannot check; ask the human")
        check_change(dest, text)


# ---------- shell commands ----------

def split_commands(cmd):
    """Commands as lists of words, split at ; && || | & and line breaks, honouring quotes."""
    cmd = re.sub(r"(?<=[\w.])\\(?=[\w.])", "/", cmd)  # Windows paths such as decisions\\x.md
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()<>\n")
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    lex.commenters = ""
    words, out = [], []
    for tok in lex:
        if tok and set(tok) <= set(";&|()\n"):
            if words:
                out.append(words)
            words = []
        else:
            words.append(tok)
    if words:
        out.append(words)
    return out


def program(words):
    """(index of the real command word, its lowercase name without folder or .exe), skipping wrappers."""
    for i, w in enumerate(words):
        name = re.split(r"[\\/]", w)[-1].lower()
        name = name[:-4] if name.endswith(".exe") else name
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", w) or name in WRAPPERS:
            continue
        return i, name
    return None, ""


def operands(words):
    return [w for w in words if not w.startswith("-") or w == "-"]


def check_targets(targets, here, removing, status_text):
    for t in targets:
        paths = rel(t, here)
        check_change(paths, removing=removing)
        if status_sensitive(paths) and STATUS_WORDS.search(status_text):
            raise Blocked(STATUS_MSG)


def check_shell(cmd, cwd, depth=0):
    if "*** Begin Patch" in cmd:
        check_patch(cmd, cwd)  # and then the rest of the command, like any other
    try:
        commands = split_commands(cmd)
    except ValueError:  # unbalanced quotes: fall back to a plain search
        if re.search(r"(^|[\s/'\"])decisions[/\\]", cmd) and (WRITE_API.search(cmd) or re.search(r"\brm\b|>", cmd)):
            raise Blocked(DECISIONS_MSG)
        return
    here = Path(cwd) if cwd else WS
    for words in commands:
        if words[0] in ("<", "<<") or (len(words) > 1 and words[0] == "<" and words[1] == "<"):
            continue
        # redirections such as > file, >> file, 1>file
        for k, w in enumerate(words):
            target = None
            m = re.fullmatch(r"(\d?|&)(>>?|>\|)([^&].*)", w)
            if w in REDIRECTS and k + 1 < len(words):
                target = words[k + 1]
            elif w == ">" and k + 1 < len(words):
                target = words[k + 1]
            elif m:
                target = m.group(3)
            if target and target.lower() not in ("/dev/null", "$null", "nul"):
                check_targets([target], here, False, " ".join(words))
        words = [w for k, w in enumerate(words)
                 if w not in (">", ">>", "<", "1>", "2>", "&>") and not (k and words[k - 1] in (">", ">>", "<", "1>", "2>", "&>"))]
        i, name = program(words)
        if i is None:
            continue
        args = words[i + 1:]
        if name in ("cd", "set-location", "pushd", "chdir", "sl") and args:
            here = here / args[0]
            continue
        if name in SHELLS and depth < 3:
            for k, a in enumerate(args):
                if a.lower() in ("-c", "-command", "/c") and k + 1 < len(args):
                    check_shell(" ".join(args[k + 1:]), here, depth + 1)
            continue
        if name in INTERPRETERS:
            script = next((a for a in args if not a.startswith("-")), None)
            inline = any(a in ("-c", "-e", "-") for a in args) or script is None or "<<" in cmd
            if script and not inline and script.replace("\\", "/").endswith("tools/review.py"):
                continue  # the governed path: review.py itself refuses what is not allowed
            code = cmd if "<<" in cmd else " ".join(args)
            if inline and WRITE_API.search(code):
                if re.search(r"(^|[^\w])decisions[/\\'\"]", code):
                    raise Blocked(DECISIONS_MSG)
                if any(g in code for g in GUARDED):
                    raise Blocked(GUARD_MSG)
                if (any(f in code for f in APPROVAL_FILES) or "proposals/" in code) and STATUS_WORDS.search(code):
                    raise Blocked(STATUS_MSG)
            continue
        if name in CHANGING:
            check_targets(operands(args), here, name in REMOVING, " ".join(args))
        elif name in COPYING:
            dest = None
            for k, a in enumerate(args):
                if a in ("-t", "--target-directory", "-destination", "-Destination") and k + 1 < len(args):
                    dest = args[k + 1]
                elif a.startswith("--target-directory="):
                    dest = a.split("=", 1)[1]
            ops = [a for a in operands(args) if a != dest]
            check_targets([dest] if dest else ops[-1:] if len(ops) >= 2 else [], here, False, " ".join(args))
        elif name in IN_PLACE and any(re.fullmatch(r"-[a-zA-Z]*i\S*|--in-place\S*", a) for a in args):
            ops = operands(args)
            files = ops[1:] if name == "sed" and not any(a in ("-e", "-f") for a in args) else ops
            check_targets(files, here, False, " ".join(args))


# ---------- entry point ----------

def check(event):
    tool = event.get("tool_name", "")
    data = event.get("tool_input") or {}
    cwd = event.get("cwd")
    if tool in EDIT_TOOLS:
        path = data.get("file_path") or data.get("notebook_path") or ""
        paths = rel(path, cwd) if path else set()
        lexical = sorted(paths)[0] if paths else None
        check_change(paths, after_edit(lexical, data) if lexical else None)
    elif tool == "apply_patch":
        cmd = data.get("command") or data.get("patch") or data.get("input") or ""
        check_patch(cmd if isinstance(cmd, str) else "\n".join(cmd), cwd)
    elif tool in SHELL_TOOLS:
        cmd = data.get("command", "")
        check_shell(cmd if isinstance(cmd, str) else " ".join(map(str, cmd)), cwd)


def main():
    raw = sys.stdin.read()
    try:
        event = json.loads(raw or "{}")
    except ValueError:
        return 0  # not a tool call we understand: leave it to the normal permission prompts
    try:
        check(event)
    except Blocked as e:
        print(f"Living System guard: blocked. {e}.", file=sys.stderr)
        return 2
    except Exception as e:  # never fail silently: block only if the call mentions a protected place
        if re.search(r"decisions|SYSTEM\.md|PRINCIPLES\.md|proposals|guard\.py|review\.py|settings\.json|hooks\.json",
                     raw):
            print(f"Living System guard: blocked, because it could not check this change ({type(e).__name__}). "
                  f"Ask the human.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

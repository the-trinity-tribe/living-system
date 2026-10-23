#!/usr/bin/env python3
"""Human review and deterministic promotion for Living System proposals.

Only an explicit `review --outcome approve` can change canonical state.
`--by` is attribution, not verified identity. Standard library only.

Two proposal kinds:
- no `kind` (default): adds an Exception to the approved decision in `target`.
- `kind: new` with `target: none`: creates a new decision from the single
  blockquote in `## Proposed future state`, titled from `# Proposal: <title>`.
"""
import argparse
import contextlib
import datetime
import hashlib
import os
import re
import stat
import sys
import tempfile
from pathlib import Path

TERMINAL = {"promoted", "rejected"}
REVIEWABLE = {"proposed", "deferred"}
OUTCOME_STATUS = {"approve": "promoted", "reject": "rejected", "defer": "deferred"}
KINDS = {"exception", "new"}


class Refusal(Exception):
    """Raised when a review must not proceed. Nothing is written."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def split_frontmatter(text, name):
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        raise Refusal(f"{name}: missing front matter")
    meta = {}
    for line in m.group(1).split("\n"):
        k, sep, v = line.partition(": ")
        if not sep or not re.fullmatch(r"[a-z_0-9]+", k) or k in meta:
            raise Refusal(f"{name}: malformed or duplicate front matter line: {line!r}")
        meta[k] = v.strip()
    return meta, m.group(1), m.group(2)


def section(body, heading, name):
    parts = re.split(r"^## (.+)$", body, flags=re.M)
    found = [parts[i + 1] for i in range(1, len(parts) - 1, 2) if parts[i].strip() == heading]
    if len(found) != 1:
        raise Refusal(f"{name}: expected exactly one '## {heading}' section, found {len(found)}")
    return found[0].strip()


def single_blockquote(text, name):
    if re.search(r"^\s*(```|~~~)", text, re.M):
        raise Refusal(f"{name}: Proposed future state must not contain a code block; write the rule as one blockquote")
    lines = text.split("\n")
    for prev, line in zip(lines, lines[1:]):
        if prev.startswith(">") and line.strip() and not line.startswith(">"):
            raise Refusal(f"{name}: every line of the proposed rule must start with '>' (found {line!r})")
    blocks = re.findall(r"(?:^>.*\n?)+", text, flags=re.M)
    if len(blocks) != 1:
        raise Refusal(f"{name}: Proposed future state must contain exactly one blockquote, found {len(blocks)}")
    quote = "\n".join(re.sub(r"^> ?", "", l) for l in blocks[0].strip().split("\n")).strip()
    if not quote:
        raise Refusal(f"{name}: Proposed future state blockquote is empty")
    if re.search(r"^\s*#", quote, re.M) or re.search(r"^\s*---\s*$", quote, re.M):
        raise Refusal(f"{name}: the proposed rule must not contain headings or '---' lines")
    return quote


def one_line(value, what):
    """Refuse values that could break into a new front-matter or log line."""
    if re.search(r"[\x00-\x1f\x7f\x85  ]", value):
        raise Refusal(f"{what} must be a single line of plain text (no line breaks or control characters)")
    return value


def decisions(root):
    out = {}
    for p in sorted((root / "decisions").glob("*.md")):
        meta, _, _ = split_frontmatter(p.read_text(encoding="utf-8"), p.relative_to(root).as_posix())
        out[p.relative_to(root).as_posix()] = meta
    return out


def superseded(root):
    return {m["supersedes"] for m in decisions(root).values()
            if m.get("status") == "approved" and "supersedes" in m}


def current_decisions(root):
    gone = superseded(root)
    return [k for k, m in decisions(root).items() if m.get("status") == "approved" and k not in gone]


def safe_rel(root, rel, prefix):
    one_line(rel, "a path")
    parts = rel.split("/")
    if (not rel.startswith(prefix) or not rel.endswith(".md") or "\\" in rel
            or any(part in ("", ".", "..") for part in parts) or len(parts) != 2):
        raise Refusal(f"path {rel!r} must be written as {prefix}<name>.md (no ./, .., \\ or subfolders)")
    p = root / rel
    if p.is_symlink() or not p.is_file():
        raise Refusal(f"{rel} does not exist or is a link")
    return p


def build_decision(root, proposal_rel, pmeta, pbody, reviewer, date):
    target_rel = pmeta["target"]
    tmeta, _, tbody = split_frontmatter((root / target_rel).read_text(encoding="utf-8"), target_rel)
    if tmeta.get("status") != "approved":
        raise Refusal(f"target {target_rel} is not approved")
    if target_rel in superseded(root):
        raise Refusal(f"target {target_rel} is already superseded; a human must re-review against the current decision")
    if sha256(root / target_rel) != pmeta.get("target_sha256"):
        raise Refusal(f"target {target_rel} changed since the proposal was written (hash mismatch); human re-review required")
    quote = single_blockquote(section(pbody, "Proposed future state", proposal_rel), proposal_rel)
    title = re.search(r"^# (.+)$", tbody, re.M)
    if not title:
        raise Refusal(f"{target_rel}: no title")
    rule, why, scope = (section(tbody, h, target_rel) for h in ("Rule", "Why", "Scope"))
    slug = Path(proposal_rel).stem[len("YYYY-MM-DD-"):]
    new_rel = f"decisions/{date}-{slug}.md"
    if (root / new_rel).exists():
        raise Refusal(f"{new_rel} already exists")
    text = (
        f"---\nstatus: approved\napproved_by: {reviewer}\ndate: {date}\n"
        f"supersedes: {target_rel}\nsource_proposal: {proposal_rel}\n---\n\n"
        f"# {title.group(1)} (amended)\n\n"
        f"## Rule\n\n{rule}\n\n### Exception\n\n{quote}\n\n"
        f"## Why\n\n{why}\n\n"
        f"## Scope\n\nSubject to the Exception under Rule.\n\n{scope}\n\n"
        f"## Provenance\n\nPromoted from `{proposal_rel}` and supersedes `{target_rel}`. "
        f"`approved_by` is attribution, not verified identity.\n"
    )
    return new_rel, text


def build_new_decision(root, proposal_rel, pbody, reviewer, date):
    titles = re.findall(r"^# Proposal: (.+)$", pbody, re.M)
    if len(titles) != 1 or not titles[0].strip():
        raise Refusal(f"{proposal_rel}: expected exactly one '# Proposal: <title>' line")
    one_line(titles[0], "the proposal title")
    quote = single_blockquote(section(pbody, "Proposed future state", proposal_rel), proposal_rel)
    slug = Path(proposal_rel).stem[len("YYYY-MM-DD-"):]
    new_rel = f"decisions/{date}-{slug}.md"
    if (root / new_rel).exists():
        raise Refusal(f"{new_rel} already exists")
    text = (
        f"---\nstatus: approved\napproved_by: {reviewer}\ndate: {date}\n"
        f"source_proposal: {proposal_rel}\n---\n\n"
        f"# {titles[0].strip()}\n\n"
        f"## Rule\n\n{quote}\n\n"
        f"## Why\n\nSee source proposal.\n\n"
        f"## Scope\n\nAs stated in the Rule.\n\n"
        f"## Provenance\n\nCreated from `{proposal_rel}`. "
        f"`approved_by` is attribution, not verified identity.\n"
    )
    return new_rel, text


def proposal_kind(meta, name):
    """Return the proposal kind, or raise if kind and target do not fit together."""
    kind = meta.get("kind", "exception")
    if kind not in KINDS:
        raise Refusal(f"{name}: unknown kind {kind!r}")
    if kind == "new":
        if meta.get("target") != "none":
            raise Refusal(f"{name}: kind: new requires target: none")
        if "target_sha256" in meta:
            raise Refusal(f"{name}: kind: new must not carry target_sha256")
    elif meta.get("target") == "none":
        raise Refusal(f"{name}: target: none requires kind: new")
    return kind


def write_all(writes):
    """Write every file or none; undo on failure.

    New files are created exclusively, so an existing file (or a link) is never
    overwritten. Existing files are replaced through a uniquely named temp file.
    """
    made_dirs, tmps, done = [], [], []
    try:
        for path in writes:
            for d in reversed([path.parent, *path.parent.parents]):
                if not d.exists():
                    d.mkdir()
                    made_dirs.append(d)
        for path, text in writes.items():
            if path.exists() or path.is_symlink():
                fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
                tmps.append(Path(tmp))
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(text)
                os.chmod(tmp, stat.S_IMODE(os.stat(path).st_mode))
                old = path.read_bytes()
                os.replace(tmp, path)
                done.append((path, old))
            else:
                try:
                    f = open(path, "x", encoding="utf-8")
                except FileExistsError:
                    raise Refusal(f"{path.name} appeared while reviewing; nothing was written") from None
                done.append((path, None))
                with f:
                    f.write(text)
    except BaseException:
        for tmp in tmps:
            tmp.unlink(missing_ok=True)
        for path, old in reversed(done):
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(old)
        for d in reversed(made_dirs):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
        raise


@contextlib.contextmanager
def review_lock(root):
    """One review at a time per workspace, so two approvals cannot race."""
    lock = root / ".review.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise Refusal("another review is running (.review.lock exists). If none is, delete .review.lock "
                      "and try again") from None
    os.close(fd)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def review(root, proposal_rel, outcome, reviewer, note="", date=None):
    root = Path(root)
    date = date or datetime.date.today().isoformat()
    if outcome not in OUTCOME_STATUS:
        raise Refusal(f"outcome must be one of {sorted(OUTCOME_STATUS)}")
    if not reviewer.strip():
        raise Refusal("--by is required")
    one_line(reviewer, "--by")
    one_line(note, "--note")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise Refusal("date must be YYYY-MM-DD")
    if not root.is_dir():
        raise Refusal(f"{root} is not a folder")
    with review_lock(root):
        return _review(root, proposal_rel, outcome, reviewer, note, date)


def _review(root, proposal_rel, outcome, reviewer, note, date):
    pp = safe_rel(root, proposal_rel, "proposals/")
    ptext = pp.read_text(encoding="utf-8")
    pmeta, pfront, pbody = split_frontmatter(ptext, proposal_rel)
    for k in ("status", "target", "evidence", "proposed_by", "date"):
        if k not in pmeta:
            raise Refusal(f"{proposal_rel}: missing front matter '{k}'")
    if pmeta["status"] in TERMINAL:
        raise Refusal(f"{proposal_rel} is already {pmeta['status']}; not reviewable again")
    if pmeta["status"] not in REVIEWABLE:
        raise Refusal(f"{proposal_rel} status {pmeta['status']!r} is not reviewable")
    kind = proposal_kind(pmeta, proposal_rel)
    if kind == "exception":
        safe_rel(root, pmeta["target"], "decisions/")

    writes = {}
    result = ""
    if outcome == "approve":
        if kind == "new":
            new_rel, new_text = build_new_decision(root, proposal_rel, pbody, reviewer, date)
        else:
            new_rel, new_text = build_decision(root, proposal_rel, pmeta, pbody, reviewer, date)
        writes[root / new_rel] = new_text
        result = new_rel
    status = OUTCOME_STATUS[outcome]
    kept = [l for l in pfront.split("\n")
            if l.split(": ")[0] not in ("reviewed_by", "reviewed_on", "resulting_decision")]
    front = re.sub(r"^status: .*$", f"status: {status}", "\n".join(kept), count=1, flags=re.M)
    front += f"\nreviewed_by: {reviewer}\nreviewed_on: {date}"
    if result:
        front += f"\nresulting_decision: {result}"
    log = f"- {date} | {outcome} | by {reviewer} (attribution, not verified)"
    if result:
        log += f" | resulting decision: {result}"
    if note:
        log += f" | note: {note}"
    pbody_new = pbody.rstrip("\n")
    if "\n## Review log\n" not in "\n" + pbody_new + "\n":
        pbody_new += "\n\n## Review log\n"
    pbody_new += f"\n{log}\n"
    writes[pp] = f"---\n{front}\n---\n{pbody_new}"
    write_all(writes)
    return status, result


def check(root):
    """Structural checks for Slice 1/2 invariants. Returns a list of problems."""
    root = Path(root)
    problems = []
    for f in ("AGENTS.md", "CONTEXT-ROUTING.md", "SYSTEM.md", "PRINCIPLES.md", "README.md"):
        if not (root / f).is_file():
            problems.append(f"missing {f}")
    routing = (root / "CONTEXT-ROUTING.md").read_text(encoding="utf-8") if (root / "CONTEXT-ROUTING.md").is_file() else ""
    for ref in re.findall(r"`((?:decisions|knowledge|projects|proposals|examples)/[^`]*|[A-Z]+\.md)`", routing):
        if not ref.endswith("/") and not (root / ref).exists():
            problems.append(f"routing points at missing {ref}")
    try:
        decs = decisions(root)
    except Refusal as e:
        return problems + [str(e)]
    for k, m in decs.items():
        if m.get("status") not in ("approved",) :
            problems.append(f"{k}: unexpected status {m.get('status')}")
        if "supersedes" in m and m["supersedes"] not in decs:
            problems.append(f"{k}: supersedes missing {m['supersedes']}")
    gone = superseded(root)
    for p in sorted((root / "projects").glob("*.md")):
        for ref in sorted(set(re.findall(r"`(decisions/[^`]*\.md)`", p.read_text(encoding="utf-8"))) & gone):
            problems.append(f"{p.relative_to(root).as_posix()}: references superseded decision {ref}")
    for p in sorted((root / "proposals").glob("*.md")):
        rel = p.relative_to(root).as_posix()
        try:
            meta, _, body = split_frontmatter(p.read_text(encoding="utf-8"), rel)
        except Refusal as e:
            problems.append(str(e))
            continue
        for k in ("status", "target", "evidence", "proposed_by", "date"):
            if k not in meta:
                problems.append(f"{rel}: missing {k}")
        try:
            kind = proposal_kind(meta, rel)
        except Refusal as e:
            problems.append(str(e))
            continue
        if kind == "exception" and meta.get("target") not in decs:
            problems.append(f"{rel}: target missing")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review")
    r.add_argument("proposal")
    r.add_argument("--outcome", required=True, choices=sorted(OUTCOME_STATUS))
    r.add_argument("--by", required=True)
    r.add_argument("--note", default="")
    r.add_argument("--date")
    sub.add_parser("current")
    h = sub.add_parser("hash")
    h.add_argument("file")
    sub.add_parser("check")
    a = ap.parse_args(argv)
    try:
        if not Path(a.root).is_dir():
            raise Refusal(f"{a.root} is not a folder")
        if a.cmd == "current" and not (Path(a.root) / "decisions").is_dir():
            raise Refusal(f"{a.root} has no decisions/ folder; is it a Living System workspace?")
        if a.cmd == "review":
            status, result = review(a.root, a.proposal, a.outcome, a.by, a.note, a.date)
            print(f"{a.proposal}: {status}" + (f"; created {result}" if result else "; canonical state unchanged"))
        elif a.cmd == "current":
            print("\n".join(current_decisions(Path(a.root))))
        elif a.cmd == "hash":
            print(sha256(Path(a.root) / a.file))
        elif a.cmd == "check":
            probs = check(a.root)
            print("\n".join(probs) if probs else "ok")
            return 1 if probs else 0
    except Refusal as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

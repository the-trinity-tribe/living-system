#!/usr/bin/env python3
"""Human review and deterministic promotion for Living System proposals.

Only an explicit `review --outcome approve` can change canonical state.
`--by` is attribution, not verified identity. Standard library only.

Proposal kinds (`kind:` in the front matter):
- none (default): adds an Exception to the current decision in `target`.
- `new`, with `target: none`: creates a decision from the single blockquote in
  `## Proposed future state`, titled from `# Proposal: <title>`.
- `replace`: a new decision whose Rule is that blockquote supersedes `target`.
- `retire`: a retirement record supersedes `target`, so no rule applies any more.
  The blockquote says why. A retirement record is never a current rule.
Every kind except `new` needs `target_sha256` of the current target.

Every review is also written to `decisions/review-record.jsonl`: one line per review with
the fingerprints of the files it wrote, each line chained to the one before. `verify`
reports any approved decision or reviewed proposal changed or deleted afterwards, any
decision the review tool did not write, and any edit to the record itself.
"""
import argparse
import contextlib
import datetime
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path

TERMINAL = {"promoted", "rejected"}
REVIEWABLE = {"proposed", "deferred"}
OUTCOME_STATUS = {"approve": "promoted", "reject": "rejected", "defer": "deferred"}
KINDS = {"exception", "new", "replace", "retire"}
RETIREMENT = "retirement"  # `kind` of a decision that only records that another one stopped applying


class Refusal(Exception):
    """Raised when a review must not proceed. Nothing is written."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


RECORD = "decisions/review-record.jsonl"
RECORD_KEYS = ("n", "date", "outcome", "by", "files", "prev", "check")


def text_sha(data):
    """Fingerprint of a text file that ignores Windows line endings (git may convert them)."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def team_workspace(root):
    """True for a shared company workspace (`"team": true` in .living/profile.json).
    A settings file that exists but cannot be read is refused, so damage never switches the team rule off."""
    path = Path(root) / ".living/profile.json"
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        data = None
    if not isinstance(data, dict):
        raise Refusal(".living/profile.json cannot be read; fix it (or restore it from git) before reviewing")
    return data.get("team") is True


def same_person(a, b):
    """The same name, ignoring case and spaces. Names are attribution, not verified identity."""
    norm = lambda s: " ".join(str(s).casefold().split())
    return norm(a) == norm(b)


def record_lines(root):
    path = Path(root) / RECORD
    if path.is_symlink() or path.parent.is_symlink():
        raise Refusal(f"{RECORD} or its folder is a link; nothing was written")
    if not path.is_file():
        return []
    return [l.rstrip("\r") for l in path.read_text(encoding="utf-8").split("\n") if l.strip()]


def record_entry(lines, date, outcome, by, files):
    """The next line of the review record: what was written, chained to the previous line."""
    entry = {"n": len(lines) + 1, "date": date, "outcome": outcome, "by": by,
             "files": {rel: text_sha(text) for rel, text in sorted(files.items())},
             "prev": text_sha(lines[-1]) if lines else "start"}
    entry["check"] = entry_check(entry)
    return json.dumps(entry, ensure_ascii=False, sort_keys=True)


def entry_check(entry):
    """Fingerprint of one record line without its own check field, so an edit to any line shows up."""
    return text_sha(json.dumps({k: v for k, v in entry.items() if k != "check"}, ensure_ascii=False, sort_keys=True))


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
    if re.search(r"^\s*(#|```|~~~)", quote, re.M) or re.search(r"^\s*---\s*$", quote, re.M):
        raise Refusal(f"{name}: the proposed rule must not contain headings, code fences or '---' lines")
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
    return [k for k, m in decisions(root).items()
            if m.get("status") == "approved" and k not in gone and m.get("kind") != RETIREMENT]


def history(root):
    """Every decision with its state, oldest first: (path, title, date, by, state). Read-only."""
    root = Path(root)
    decs = decisions(root)
    replaced_by = {m["supersedes"]: k for k, m in decs.items() if m.get("status") == "approved" and "supersedes" in m}
    current = set(current_decisions(root))
    out = []
    for k, m in sorted(decs.items(), key=lambda kv: (kv[1].get("date", ""), kv[0])):
        body = split_frontmatter((root / k).read_text(encoding="utf-8"), k)[2]
        title = (re.search(r"^# (.+)$", body, re.M) or re.match("(.*)", Path(k).stem)).group(1).strip()
        if m.get("kind") == RETIREMENT:
            state = f"retirement record for {m.get('supersedes', '?')}"
        elif k in current:
            state = "in force"
        elif k in replaced_by:
            later = decs[replaced_by[k]]
            how = ("retired" if later.get("kind") == RETIREMENT else
                   "amended" if "\n### Exception\n" in (root / replaced_by[k]).read_text(encoding="utf-8") else "replaced")
            state = f"{how} by {replaced_by[k]} on {later.get('date', '?')}"
        else:
            state = f"not in force (status: {m.get('status')})"
        out.append((k, title, m.get("date", "?"), m.get("approved_by", "?"), state))
    return out


def format_history(rows):
    if not rows:
        return "No decisions yet."
    lines = []
    for k, title, date, by, state in rows:
        lines.append(f"{date}  {title}\n            {k}\n            {state}; approved by {by} (attribution, not verified)")
    return "\n".join(lines)


def safe_rel(root, rel, prefix):
    one_line(rel, "a path")
    parts = rel.split("/")
    if (not rel.startswith(prefix) or not rel.endswith(".md") or "\\" in rel
            or any(part in ("", ".", "..") for part in parts) or len(parts) != 2):
        raise Refusal(f"path {rel!r} must be written as {prefix}<name>.md (no ./, .., \\ or subfolders)")
    folder = root / parts[0]
    p = root / rel
    if folder.is_symlink() or p.is_symlink() or not p.is_file():
        raise Refusal(f"{rel} does not exist, or it or its folder is a link")
    if parts[1] not in os.listdir(folder):  # Windows and macOS ignore case; the recorded name must match exactly
        raise Refusal(f"{rel} is spelled differently from the file on disk (check capital letters)")
    return p


def checked_target(root, pmeta):
    """The target decision, if it is current, unchanged since the proposal, and a real rule."""
    target_rel = pmeta["target"]
    tmeta, _, tbody = split_frontmatter((root / target_rel).read_text(encoding="utf-8"), target_rel)
    if tmeta.get("status") != "approved":
        raise Refusal(f"target {target_rel} is not approved")
    if tmeta.get("kind") == RETIREMENT:
        raise Refusal(f"target {target_rel} only records a retirement; propose kind: new to bring a rule back")
    if target_rel in superseded(root):
        raise Refusal(f"target {target_rel} is already superseded; a human must re-review against the current decision")
    if sha256(root / target_rel) != pmeta.get("target_sha256"):
        raise Refusal(f"target {target_rel} changed since the proposal was written (hash mismatch); human re-review required")
    return tmeta, tbody


def new_decision_path(root, proposal_rel, date):
    # Proposals are named YYYY-MM-DD-short-name.md; the decision keeps the short name. Other names keep the whole stem.
    stem = Path(proposal_rel).stem
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    if not slug or slug.startswith("."):
        raise Refusal(f"{proposal_rel}: rename it to YYYY-MM-DD-short-name.md so the decision gets a name")
    new_rel = f"decisions/{date}-{slug}.md"
    if (root / new_rel).exists() or (root / new_rel).is_symlink():
        raise Refusal(f"{new_rel} already exists")
    return new_rel


def proposal_title(pbody, proposal_rel):
    titles = re.findall(r"^# Proposal: (.+)$", pbody, re.M)
    if len(titles) != 1 or not titles[0].strip():
        raise Refusal(f"{proposal_rel}: expected exactly one '# Proposal: <title>' line")
    return one_line(titles[0].strip(), "the proposal title")


def build_decision(root, proposal_rel, pmeta, pbody, reviewer, date):
    target_rel = pmeta["target"]
    tmeta, tbody = checked_target(root, pmeta)
    quote = single_blockquote(section(pbody, "Proposed future state", proposal_rel), proposal_rel)
    title = re.search(r"^# (.+)$", tbody, re.M)
    if not title:
        raise Refusal(f"{target_rel}: no title")
    rule, why, scope = (section(tbody, h, target_rel) for h in ("Rule", "Why", "Scope"))
    new_rel = new_decision_path(root, proposal_rel, date)
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
    title = proposal_title(pbody, proposal_rel)
    quote = single_blockquote(section(pbody, "Proposed future state", proposal_rel), proposal_rel)
    new_rel = new_decision_path(root, proposal_rel, date)
    text = (
        f"---\nstatus: approved\napproved_by: {reviewer}\ndate: {date}\n"
        f"source_proposal: {proposal_rel}\n---\n\n"
        f"# {title}\n\n"
        f"## Rule\n\n{quote}\n\n"
        f"## Why\n\nSee source proposal.\n\n"
        f"## Scope\n\nAs stated in the Rule.\n\n"
        f"## Provenance\n\nCreated from `{proposal_rel}`. "
        f"`approved_by` is attribution, not verified identity.\n"
    )
    return new_rel, text


def build_replacement(root, proposal_rel, pmeta, pbody, reviewer, date):
    target_rel = pmeta["target"]
    checked_target(root, pmeta)
    title = proposal_title(pbody, proposal_rel)
    quote = single_blockquote(section(pbody, "Proposed future state", proposal_rel), proposal_rel)
    new_rel = new_decision_path(root, proposal_rel, date)
    text = (
        f"---\nstatus: approved\napproved_by: {reviewer}\ndate: {date}\n"
        f"supersedes: {target_rel}\nsource_proposal: {proposal_rel}\n---\n\n"
        f"# {title}\n\n"
        f"## Rule\n\n{quote}\n\n"
        f"## Why\n\nSee source proposal.\n\n"
        f"## Scope\n\nAs stated in the Rule.\n\n"
        f"## Provenance\n\nPromoted from `{proposal_rel}`. Replaces `{target_rel}`, which stays as history. "
        f"`approved_by` is attribution, not verified identity.\n"
    )
    return new_rel, text


def build_retirement(root, proposal_rel, pmeta, pbody, reviewer, date):
    target_rel = pmeta["target"]
    _, tbody = checked_target(root, pmeta)
    title = re.search(r"^# (.+)$", tbody, re.M)
    if not title:
        raise Refusal(f"{target_rel}: no title")
    reason = single_blockquote(section(pbody, "Proposed future state", proposal_rel), proposal_rel)
    new_rel = new_decision_path(root, proposal_rel, date)
    text = (
        f"---\nstatus: approved\nkind: {RETIREMENT}\napproved_by: {reviewer}\ndate: {date}\n"
        f"supersedes: {target_rel}\nsource_proposal: {proposal_rel}\n---\n\n"
        f"# Retired: {title.group(1)}\n\n"
        f"This record is not a rule. From {date}, `{target_rel}` no longer applies, and no rule replaces it.\n\n"
        f"## Why\n\n{reason}\n\n"
        f"## Provenance\n\nPromoted from `{proposal_rel}`. `{target_rel}` stays as history. "
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


def write_all(writes, new=()):
    """Write every file or none; undo on failure.

    Paths in `new` are created exclusively, so an existing file (or a link) is
    never overwritten, even one that appeared after validation. Other paths must
    already exist and are replaced through a uniquely named temp file.
    """
    made_dirs, tmps, done = [], [], []
    try:
        for path in writes:
            for d in reversed([path.parent, *path.parent.parents]):
                if not d.exists():
                    d.mkdir()
                    made_dirs.append(d)
        for path, text in writes.items():
            if path not in new:
                fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
                tmps.append(Path(tmp))
                with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                    f.write(text)
                os.chmod(tmp, stat.S_IMODE(os.stat(path).st_mode))
                old = path.read_bytes()
                os.replace(tmp, path)
                done.append((path, old))
            else:
                try:
                    f = open(path, "x", encoding="utf-8", newline="\n")
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
    if kind != "new":
        safe_rel(root, pmeta["target"], "decisions/")
    if outcome == "approve" and team_workspace(root) and same_person(reviewer, pmeta["proposed_by"]):
        raise Refusal(f"this is a team workspace: {reviewer} proposed this change, so someone else approves it "
                      f"(the person who makes a change does not check it). Rejecting or deferring it yourself is fine")

    writes = {}
    result = ""
    if outcome == "approve":
        if kind == "new":
            new_rel, new_text = build_new_decision(root, proposal_rel, pbody, reviewer, date)
        else:
            build = {"exception": build_decision, "replace": build_replacement, "retire": build_retirement}[kind]
            new_rel, new_text = build(root, proposal_rel, pmeta, pbody, reviewer, date)
        if (root / "decisions").is_symlink():
            raise Refusal("decisions/ is a link; nothing was written")
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
    lines = record_lines(root)
    files = {p.relative_to(root).as_posix(): text for p, text in writes.items()}
    record = root / RECORD
    writes[record] = "".join(l + "\n" for l in lines) + record_entry(lines, date, outcome, reviewer, files) + "\n"
    new = {root / result} if result else set()
    write_all(writes, new=new | (set() if record.is_file() else {record}))
    return status, result


def start_record(root, by, date=None):
    """Start the review record for a workspace that has none: fingerprint what is there now. Returns the file count."""
    root = Path(root)
    date = date or datetime.date.today().isoformat()
    one_line(by, "--by")
    if not by.strip():
        raise Refusal("--by is required")
    if not (root / "decisions").is_dir():
        raise Refusal(f"{root} has no decisions/ folder")
    with review_lock(root):
        if record_lines(root) or (root / RECORD).exists():
            raise Refusal(f"{RECORD} already exists; a record is started only once. Run verify to check it")
        files = {}
        for p in sorted((root / "decisions").glob("*.md")) + sorted((root / "proposals").glob("*.md")):
            rel = p.relative_to(root).as_posix()
            if rel.startswith("proposals/"):
                meta = split_frontmatter(p.read_text(encoding="utf-8"), rel)[0]
                if meta.get("status") not in TERMINAL | {"deferred"}:
                    continue  # still open: nothing has been decided about it yet
            files[rel] = p.read_text(encoding="utf-8")
        write_all({root / RECORD: record_entry([], date, "start", by, files) + "\n"}, new={root / RECORD})
    return len(files)


def verify(root):
    """[(level, message)] comparing decisions and reviewed proposals with the review record. Read-only."""
    root = Path(root)
    if (root / ".review.lock").exists():
        return [("INFO", "a review is running right now; run verify again when it has finished")]
    try:
        lines = record_lines(root)
    except Refusal as e:
        return [("ERROR", str(e))]
    if not lines and not any((root / "decisions").glob("*.md")):
        return []  # nothing decided yet: the record starts with the first review
    if not lines:
        return [("INFO", f"no review record yet ({RECORD}); it starts with the next review, or run: "
                         f"python3 tools/review.py verify --start --by \"Your Name\"")]
    out, latest, prev = [], {}, "start"
    for i, line in enumerate(lines, 1):
        try:
            e = json.loads(line)
            ok = isinstance(e, dict) and all(k in e for k in RECORD_KEYS) and isinstance(e["files"], dict)
        except ValueError:
            ok = False
        if not ok or e["n"] != i or e["prev"] != prev or e["check"] != entry_check(e):
            return [("ERROR", f"{RECORD} line {i} was edited, removed or added by hand; the record cannot be "
                              f"trusted from there on. Restore it from git or a backup")]
        prev = text_sha(line)
        for rel, sha in e["files"].items():
            latest[rel] = (sha, e["date"], e["outcome"])
    for rel, (sha, date, outcome) in sorted(latest.items()):
        p = root / rel
        what = "approved decision" if rel.startswith("decisions/") else "reviewed proposal"
        if not p.is_file():
            out.append(("ERROR", f"{rel}: {what} from {date} is missing"))
        elif text_sha(p.read_bytes()) != sha:
            out.append(("ERROR", f"{rel}: {what} was changed after it was recorded on {date} ({outcome})"))
    for p in sorted((root / "decisions").glob("*.md")):
        rel = p.relative_to(root).as_posix()
        if rel not in latest:
            out.append(("WARN", f"{rel}: not written by the review tool (by hand, or before the record started); "
                                f"check who wrote it"))
    for p in sorted((root / "proposals").glob("*.md")) if (root / "proposals").is_dir() else []:
        rel = p.relative_to(root).as_posix()
        try:
            status = split_frontmatter(p.read_text(encoding="utf-8"), rel)[0].get("status")
        except (Refusal, UnicodeDecodeError):
            continue
        if rel not in latest and status in TERMINAL | {"deferred"}:
            out.append(("WARN", f"{rel}: marked {status}, but no review of it is in the record (set by hand, or "
                                f"before the record started); check who changed it"))
    return out


def format_verify(results, root):
    if not results:
        n = len(record_lines(root))
        return f"Review record intact: {n} entr{'y' if n == 1 else 'ies'}; every recorded file is unchanged."
    return "\n".join(f"{lvl}: {msg}" for lvl, msg in results)


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
        if m.get("kind") not in (None, RETIREMENT):
            problems.append(f"{k}: unexpected kind {m.get('kind')}")
        if m.get("kind") == RETIREMENT and "supersedes" not in m:
            problems.append(f"{k}: a retirement record must name the decision it retires in supersedes")
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
        if kind != "new" and meta.get("target") not in decs:
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
    sub.add_parser("history", help="every decision, oldest first, with what changed it")
    h = sub.add_parser("hash")
    h.add_argument("file")
    sub.add_parser("check")
    v = sub.add_parser("verify", help="check that no approved decision or reviewed proposal changed afterwards")
    v.add_argument("--start", action="store_true", help="start the record for a workspace that has none")
    v.add_argument("--by", help="with --start: who starts it")
    a = ap.parse_args(argv)
    a.root = os.path.expanduser(a.root)  # PowerShell passes ~ through unexpanded
    try:
        if not Path(a.root).is_dir():
            raise Refusal(f"{a.root} is not a folder")
        if a.cmd in ("current", "history", "verify") and not (Path(a.root) / "decisions").is_dir():
            raise Refusal(f"{a.root} has no decisions/ folder; is it a Living System workspace?")
        if a.cmd == "review":
            status, result = review(a.root, a.proposal, a.outcome, a.by, a.note, a.date)
            print(f"{a.proposal}: {status}" + (f"; created {result}" if result else "; canonical state unchanged"))
        elif a.cmd == "history":
            print(format_history(history(Path(a.root))))
        elif a.cmd == "current":
            print("\n".join(current_decisions(Path(a.root))))
        elif a.cmd == "hash":
            print(sha256(Path(a.root) / a.file))
        elif a.cmd == "verify":
            if a.start:
                n = start_record(a.root, a.by or "")
                print(f"Started {RECORD} with {n} file(s). From now on, verify reports any change to them.")
                return 0
            results = verify(a.root)
            print(format_verify(results, a.root))
            return 1 if any(lvl == "ERROR" for lvl, _ in results) else 0
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

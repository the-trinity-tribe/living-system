#!/usr/bin/env python3
"""Human review and deterministic promotion for Living System proposals.

Only an explicit `review --outcome approve` can change canonical state.
`--by` is attribution, not verified identity. Standard library only.
"""
import argparse
import datetime
import hashlib
import re
import sys
from pathlib import Path

TERMINAL = {"promoted", "rejected"}
REVIEWABLE = {"proposed", "deferred"}
OUTCOME_STATUS = {"approve": "promoted", "reject": "rejected", "defer": "deferred"}


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
    blocks = re.findall(r"(?:^>.*\n?)+", text, flags=re.M)
    if len(blocks) != 1:
        raise Refusal(f"{name}: Proposed future state must contain exactly one blockquote, found {len(blocks)}")
    quote = "\n".join(re.sub(r"^> ?", "", l) for l in blocks[0].strip().split("\n")).strip()
    if not quote:
        raise Refusal(f"{name}: Proposed future state blockquote is empty")
    return quote


def decisions(root):
    out = {}
    for p in sorted((root / "decisions").glob("*.md")):
        meta, _, _ = split_frontmatter(p.read_text(), str(p.relative_to(root)))
        out[str(p.relative_to(root))] = meta
    return out


def superseded(root):
    return {m["supersedes"] for m in decisions(root).values()
            if m.get("status") == "approved" and "supersedes" in m}


def current_decisions(root):
    gone = superseded(root)
    return [k for k, m in decisions(root).items() if m.get("status") == "approved" and k not in gone]


def safe_rel(root, rel, prefix):
    if not rel.startswith(prefix) or ".." in Path(rel).parts or not rel.endswith(".md"):
        raise Refusal(f"path {rel!r} must be a .md file under {prefix}")
    p = root / rel
    if not p.is_file():
        raise Refusal(f"{rel} does not exist")
    return p


def build_decision(root, proposal_rel, pmeta, pbody, reviewer, date):
    target_rel = pmeta["target"]
    tmeta, _, tbody = split_frontmatter((root / target_rel).read_text(), target_rel)
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


def review(root, proposal_rel, outcome, reviewer, note="", date=None):
    root = Path(root)
    date = date or datetime.date.today().isoformat()
    if outcome not in OUTCOME_STATUS:
        raise Refusal(f"outcome must be one of {sorted(OUTCOME_STATUS)}")
    if not reviewer.strip() or "\n" in reviewer or "\n" in note:
        raise Refusal("--by is required; --by and --note must be single-line")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise Refusal("date must be YYYY-MM-DD")
    pp = safe_rel(root, proposal_rel, "proposals/")
    ptext = pp.read_text()
    pmeta, pfront, pbody = split_frontmatter(ptext, proposal_rel)
    for k in ("status", "target", "evidence", "proposed_by", "date"):
        if k not in pmeta:
            raise Refusal(f"{proposal_rel}: missing front matter '{k}'")
    if pmeta["status"] in TERMINAL:
        raise Refusal(f"{proposal_rel} is already {pmeta['status']}; not reviewable again")
    if pmeta["status"] not in REVIEWABLE:
        raise Refusal(f"{proposal_rel} status {pmeta['status']!r} is not reviewable")
    safe_rel(root, pmeta["target"], "decisions/")

    writes = {}
    result = ""
    if outcome == "approve":
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
    for path, text in writes.items():
        with open(path, "x" if not path.exists() else "w") as f:
            f.write(text)
    return status, result


def check(root):
    """Structural checks for Slice 1/2 invariants. Returns a list of problems."""
    root = Path(root)
    problems = []
    for f in ("AGENTS.md", "CONTEXT-ROUTING.md", "SYSTEM.md", "PRINCIPLES.md", "README.md"):
        if not (root / f).is_file():
            problems.append(f"missing {f}")
    routing = (root / "CONTEXT-ROUTING.md").read_text() if (root / "CONTEXT-ROUTING.md").is_file() else ""
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
        for ref in sorted(set(re.findall(r"`(decisions/[^`]*\.md)`", p.read_text())) & gone):
            problems.append(f"{p.relative_to(root)}: references superseded decision {ref}")
    for p in sorted((root / "proposals").glob("*.md")):
        rel = str(p.relative_to(root))
        try:
            meta, _, body = split_frontmatter(p.read_text(), rel)
        except Refusal as e:
            problems.append(str(e))
            continue
        for k in ("status", "target", "evidence", "proposed_by", "date"):
            if k not in meta:
                problems.append(f"{rel}: missing {k}")
        if meta.get("target") not in decs:
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

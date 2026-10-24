"""Laya vs keyword rules on three Living System decisions. Prints a JSON summary.

Not part of Living System and not run by its tests. Needs: pip install torch laya (see README.md).
Run: python bench.py keywords | english | multilingual
"""
import json, re, resource, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cases import CASES

REPO = Path(__file__).resolve().parents[3]
MODS = {}
for d in sorted((REPO / "modules").iterdir()):
    if (d / "module.json").is_file():
        m = json.loads((d / "module.json").read_text(encoding="utf-8"))
        MODS[m["id"]] = m

# ---- baselines: the shipped signal phrases, and short keyword lists written before any model run ----
RISK_WORDS = r"\b(publish|post |send|email|pay|buy|delete|remove|lösche|veröffentlich|zapłać|usuń|wyślij|rule|approve|company workspace|migrat|move the whole|przenosimy|moving the whole|billing|database|across the repository|restructur)"
REPEAT_WORDS = r"\b(week|weekly|every|monthly|month|friday|again|each|newsletter|tygodni|woche|wöchentlich|freitag|piątek|notes|notizen|notatki|minutes|stand-up|call|post|client|kunde|klient|unternehmen)"


def keyword_module(text):
    low = text.lower()
    for mid, m in MODS.items():
        if any(s.lower() in low for s in m["signals"]):
            return mid
    return "none"


def keyword_risk(text):
    return "high" if re.search(RISK_WORDS, text.lower()) else "low"


def keyword_repeat(text):
    return bool(re.search(REPEAT_WORDS, text.lower()))


QUESTIONS = {
    "module": {"type": "choice", "instructions": "Which optional workflow module fits this request best? Choose none if no module is needed.",
               "criteria": {**{mid: m["summary"] for mid, m in MODS.items()},
                            "none": "No module: a quick question, a one-off edit, or something no module covers."}},
    "risk": {"type": "choice", "instructions": "Is this request high risk? High risk means it publishes, sends to people, spends money, deletes something, changes rules or approvals, touches the company workspace, or changes many files.",
             "criteria": {"high": "It publishes, sends, spends, deletes, changes rules or approvals, or changes many files.",
                          "low": "It only drafts, reads, explains or makes a small reversible edit."}},
    "repeats": {"type": "noul", "instructions": "Is this a kind of work that usually repeats (for example a weekly update, notes after calls, a monthly report, a newsletter)?",
                "criteria": {"false": "A one-off task or question.", "true": "Work that comes back regularly."}},
}


def score(preds):
    n = len(CASES)
    out = {}
    for k, idx in (("module", 1), ("risk", 2), ("repeats", 3)):
        out[k] = round(sum(1 for p, c in zip(preds, CASES) if p[k] == c[idx]) / n, 3)
    for name, rng in (("en", range(0, 60)), ("de_pl", range(60, n))):
        out[f"module_{name}"] = round(sum(1 for i in rng if preds[i]["module"] == CASES[i][1]) / len(rng), 3)
    hi = [i for i, c in enumerate(CASES) if c[2] == "high"]
    out["high_risk_recall"] = round(sum(1 for i in hi if preds[i]["risk"] == "high") / len(hi), 3)
    return out


def run_keywords():
    preds = [{"module": keyword_module(c[0]), "risk": keyword_risk(c[0]), "repeats": keyword_repeat(c[0])} for c in CASES]
    return score(preds), preds


def run_laya(subfolder=None, threshold=0.5):
    import laya, torch
    torch.set_num_threads(8)
    t0 = time.time()
    agent = laya.load("convaiinnovations/laya", subfolder=subfolder, device="cpu")
    load_s = time.time() - t0
    preds, times, confs = [], [], []
    agent.predict({"request": "warm up"}, QUESTIONS)
    for c in CASES:
        t = time.time()
        r = agent.predict({"request": c[0]}, QUESTIONS)
        times.append(time.time() - t)
        a = r["answers"]
        conf = {"module": a["module"].get("answer_confidence") if isinstance(a["module"], dict) else None}
        preds.append({"module": a["module"]["choice"] if isinstance(a["module"], dict) else a["module"],
                      "risk": a["risk"]["choice"] if isinstance(a["risk"], dict) else a["risk"],
                      "repeats": (a["repeats"]["noul"] if isinstance(a["repeats"], dict) else a["repeats"]) >= threshold})
        confs.append(conf.get("module") if isinstance(conf, dict) else None)
    s = score(preds)
    times.sort()
    s.update(load_seconds=round(load_s, 1), median_ms=round(1000 * times[len(times) // 2]),
             p90_ms=round(1000 * times[int(len(times) * 0.9)]),
             peak_rss_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
    # confidence vs correctness for the module question
    pairs = [(cf, p["module"] == c[1]) for cf, p, c in zip(confs, preds, CASES) if isinstance(cf, (int, float))]
    if pairs:
        pairs.sort(reverse=True)
        top = pairs[: max(1, len(pairs) // 3)]
        s["module_acc_top_third_by_confidence"] = round(sum(ok for _, ok in top) / len(top), 3)
        s["module_kept_at_conf_0.5"] = sum(1 for cf, _ in pairs if cf >= 0.5)
        kept = [ok for cf, ok in pairs if cf >= 0.5]
        s["module_acc_when_conf_0.5"] = round(sum(kept) / len(kept), 3) if kept else None
    return s, preds, r


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "keywords":
        s, preds = run_keywords()
        print(json.dumps({"keywords": s}))
    else:
        s, preds, last = run_laya(None if which == "english" else "multilingual")
        sample = {k: v for k, v in last.items() if k in ("answers", "confidence", "probabilities", "routing")}
        print(json.dumps({which: s, "sample_output_keys": list(last.keys()), "sample": sample}, default=str)[:4000])
        Path(f"preds-{which}.json").write_text(json.dumps(preds))

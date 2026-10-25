#!/usr/bin/env python3
"""Deterministic half of the slice-C ledger audit. Read-only on the repo.

    python3 -I ledger_audit.py census            -> census.json
    python3 -I ledger_audit.py audit IDS... --out FILE
    python3 -I ledger_audit.py audit --shard FILE --out FILE   (FILE: one id per line)

For each evidence record it records facts only; verdicts are composed later.
A check that cannot be made yields null, never True.
"""
from __future__ import annotations
import glob, hashlib, json, os, re, subprocess, sys
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[4]
ENUM = {"anecdotal", "preliminary", "replicated", "strong", "inconclusive", "contradictory"}
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
RUNTOK = re.compile(r"\bRUN-[A-Za-z0-9][A-Za-z0-9_.-]*[A-Za-z0-9]\b")
TIMEKEY = re.compile(r"time|wall|date|host|pid|elapsed|seconds|second|stamp|duration|uuid|commit", re.I)


def load(p: Path):
    try:
        d = yaml.safe_load(p.read_text())
    except Exception as e:  # noqa
        return None, f"parse_error: {str(e)[:80]}"
    if isinstance(d, dict) and isinstance(d.get("evidence"), dict):
        return d["evidence"], None
    return d, None


def classify(ev, err):
    if err:
        return "malformed_parse_error", None
    if not isinstance(ev, dict):
        return "malformed_not_mapping", None
    s = ev.get("strength")
    if s is None:
        return "malformed_missing", None
    if not isinstance(s, str):
        return "malformed_nonstring", repr(s)[:80]
    if s in ("replicated", "strong"):
        return s, s
    if s == "moderate":
        return "moderate", s
    if s in ("preliminary", "inconclusive"):
        return s, s
    if s == "n/a":
        return "malformed_na", s
    return "malformed_other", s


_run_index = None


def run_index():
    global _run_index
    if _run_index is None:
        idx = {}
        for d in glob.glob(str(REPO / "experiments/*/runs/*")):
            if os.path.isdir(d):
                idx.setdefault(os.path.basename(d), []).append(d)
        _run_index = idx
    return _run_index


_mut = None


def mutated_runs():
    """run dirs with any committed Modify/Delete after their add (git history)."""
    global _mut
    if _mut is None:
        out = subprocess.run(["git", "-C", str(REPO), "log", "--no-renames", "--diff-filter=MD",
                              "--name-status", "--format=C %h", "--", "experiments/*/runs/*"],
                             capture_output=True, text=True).stdout
        m = {}
        c = ""
        for ln in out.splitlines():
            if ln.startswith("C "):
                c = ln[2:]
            elif ln and ln[0] in "MD":
                parts = ln.split("\t", 1)[1].split("/")
                if len(parts) > 3 and parts[2] == "runs":
                    m.setdefault(parts[3], set()).add(f"{ln[0]}:{c}")
        _mut = m
    return _mut


def sha256(p: Path):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def digests_in_run(rdir: Path):
    """Find declared (path, sha256) pairs in a run directory and verify them."""
    res = {"declared": 0, "ok": 0, "mismatch": [], "unresolvable": 0}
    files = [p for p in rdir.rglob("*") if p.is_file() and p.stat().st_size < 4_000_000
             and p.suffix in (".yaml", ".yml", ".json", ".sha256", ".txt", ".sha256sum", ".md")]
    for p in files[:400]:
        try:
            txt = p.read_text(errors="ignore")
        except Exception:
            continue
        if not HEX64.search(txt):
            continue
        pairs = []
        if p.suffix in (".sha256", ".sha256sum", ".txt"):
            for ln in txt.splitlines():
                m = re.match(r"^\s*([0-9a-f]{64})\s+\*?(.+?)\s*$", ln)
                if m:
                    pairs.append((m.group(2), m.group(1)))
        else:
            try:
                obj = yaml.safe_load(txt)
            except Exception:
                obj = None

            def walk(o):
                if isinstance(o, dict):
                    dig = None
                    for k, v in o.items():
                        if isinstance(v, str) and re.fullmatch(r"(sha256:)?[0-9a-f]{64}", v) and \
                                re.search(r"sha|digest|hash", str(k), re.I):
                            dig = v.replace("sha256:", "")
                    path = None
                    for k in ("path", "file", "artifact", "name", "relpath", "filename"):
                        if isinstance(o.get(k), str):
                            path = o[k]
                            break
                    if dig and path:
                        pairs.append((path, dig))
                    for v in o.values():
                        walk(v)
                elif isinstance(o, list):
                    for v in o:
                        walk(v)
            walk(obj)
        for path, dig in pairs:
            res["declared"] += 1
            cand = [rdir / path, REPO / path, p.parent / path]
            hit = next((c for c in cand if c.is_file()), None)
            if hit is None:
                res["unresolvable"] += 1
            elif sha256(hit) == dig:
                res["ok"] += 1
            else:
                res["mismatch"].append(f"{p.name}:{path}")
    return res


def refs_of(ev):
    out = []
    for k in ("proof_refs", "certificate_refs", "review_refs"):
        v = ev.get(k)
        if isinstance(v, list):
            for x in v:
                if isinstance(x, str):
                    out.append(x)
                elif isinstance(x, dict):
                    for vv in x.values():
                        if isinstance(vv, str) and "/" in vv:
                            out.append(vv)
        elif isinstance(v, str):
            out.append(v)
    return out


def pathlike(s):
    s = s.strip().split(" ")[0].split("#")[0].split("::")[0]
    return s if re.search(r"\.[A-Za-z0-9]{1,6}$", s) and " " not in s and not s.startswith("http") else None


def numbers(text):
    return set(re.findall(r"(?<![\w.])-?\d+\.\d{3,}(?![\w])", text))


def audit_one(eid):
    p = REPO / "ledger/evidence" / f"{eid}.yaml"
    ev, err = load(p)
    cls, raw = classify(ev, err)
    row = {"evidence_id": eid, "class": cls, "strength_raw": raw}
    if not isinstance(ev, dict):
        row.update(parse_error=err)
        return row
    runs = ev.get("run_ids") if isinstance(ev.get("run_ids"), list) else []
    runs = [r for r in runs if isinstance(r, str)]
    text = p.read_text()
    text_runs = sorted(set(RUNTOK.findall(text)) - set(runs))
    idx = run_index()
    found = {r: idx.get(r, []) for r in runs}
    row["run_ids_declared"] = len(runs)
    row["runs_found"] = sum(1 for r in runs if found[r])
    row["runs_missing"] = [r for r in runs if not found[r]][:10]
    row["runs_dup_dirs"] = [r for r in runs if len(found[r]) > 1][:5]
    row["text_run_tokens_resolved"] = sum(1 for r in text_runs if idx.get(r))
    row["text_run_tokens_unresolved"] = [r for r in text_runs if not idx.get(r)][:10]
    exps = ev.get("experiment_ids") if isinstance(ev.get("experiment_ids"), list) else []
    row["experiment_ids"] = len(exps)
    row["experiments_found"] = sum(1 for e in exps if isinstance(e, str) and (REPO / "experiments" / e).is_dir())
    refs = [pathlike(x) for x in refs_of(ev)]
    refs = [r for r in refs if r]
    row["refs_declared"] = len(refs)
    row["refs_found"] = sum(1 for r in refs if (REPO / r).exists())
    row["refs_missing"] = [r for r in refs if not (REPO / r).exists()][:6]
    # digests + immutability
    d = {"declared": 0, "ok": 0, "mismatch": [], "unresolvable": 0}
    mut = {}
    runtext = ""
    for r in runs:
        for dd in found[r][:1]:
            x = digests_in_run(Path(dd))
            d["declared"] += x["declared"]
            d["ok"] += x["ok"]
            d["unresolvable"] += x["unresolvable"]
            d["mismatch"] += x["mismatch"]
            if r in mutated_runs():
                mut[r] = sorted(mutated_runs()[r])[:3]
            for f in list(Path(dd).rglob("*"))[:60]:
                if f.is_file() and f.suffix in (".yaml", ".json", ".md", ".txt") and f.stat().st_size < 600_000:
                    runtext += f.read_text(errors="ignore")
    row["digests"] = d
    row["digests_ok"] = (None if d["declared"] == 0 else (len(d["mismatch"]) == 0 and d["ok"] > 0))
    row["runs_mutated_after_add"] = mut
    # number tracing (NOT recomputation)
    claimtext = yaml.safe_dump({k: ev.get(k) for k in ("observations", "inference", "interpretation", "boundaries") if k in ev})
    nums = numbers(claimtext)
    traced = [n for n in nums if n in runtext] if runtext else []
    row["numbers_claimed"] = len(nums)
    row["numbers_traced_to_run_artifacts"] = len(traced)
    # independence signals
    sig = {}
    blob = yaml.safe_dump({k: ev.get(k) for k in ("reviewed_by", "validator_verdict", "review_refs", "red_team_reviewed",
                                                  "review_verdicts", "independent_review_required", "independent_review_note")
                           if k in ev})
    sig["validator"] = bool(re.search(r"validator|validation[_ ]report", blob, re.I))
    sig["red_team"] = bool(re.search(r"red[-_ ]?team", blob, re.I))
    sig["reviewed_by"] = ev.get("reviewed_by") if isinstance(ev.get("reviewed_by"), (str, list)) else None
    sig["producer_tasks"] = ev.get("source_task_ids") if isinstance(ev.get("source_task_ids"), dict) else None
    rr = [pathlike(x) for x in (ev.get("review_refs") or []) if isinstance(x, str)] if isinstance(ev.get("review_refs"), list) else []
    sig["review_refs_found"] = sum(1 for x in rr if x and (REPO / x).exists())
    sig["review_refs_declared"] = len([x for x in rr if x])
    row["independence_signals"] = sig
    # lean
    lean = [r for r in refs if r.endswith(".lean") and (REPO / r).exists()]
    holes = []
    for r in lean:
        t = (REPO / r).read_text(errors="ignore")
        t = re.sub(r"--.*", "", t)
        for w in ("sorry", "native_decide", "ofReduceBool", r"\baxiom\b", "admit"):
            if re.search(w, t):
                holes.append(f"{r}:{w}")
    row["lean_files"] = len(lean)
    row["lean_holes"] = holes[:8]
    # replay eligibility
    elig = None
    for r in runs:
        for dd in found[r][:1]:
            cmd = Path(dd) / "command.txt"
            if cmd.exists():
                elig = str(cmd.relative_to(REPO))
    row["replay_command_file"] = elig
    row["claim_tier"] = ev.get("claim_tier")
    row["type"] = ev.get("type")
    row["has_boundaries"] = bool(ev.get("boundaries"))
    row["has_confounds"] = bool(ev.get("unresolved_confounds"))
    return row


def main():
    a = sys.argv[1:]
    if a and a[0] == "census":
        out = {}
        for p in sorted((REPO / "ledger/evidence").glob("*.yaml")):
            ev, err = load(p)
            cls, raw = classify(ev, err)
            out[p.stem] = {"class": cls, "strength_raw": raw}
        json.dump(out, open(a[1], "w"), indent=0)
        return
    if a and a[0] == "audit":
        outf = a[a.index("--out") + 1]
        if "--shard" in a:
            ids = [x.strip() for x in open(a[a.index("--shard") + 1]) if x.strip()]
        else:
            ids = [x for x in a[1:a.index("--out")]]
        with open(outf, "w") as f:
            for i in ids:
                f.write(json.dumps(audit_one(i)) + "\n")
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()

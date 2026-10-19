#!/usr/bin/env python3
"""Strict replay comparator (supersedes the normaliser in replay.py, which is kept only as
the provenance of the historical rows in shards/replay_out*.jsonl).

Equality is exact on every leaf (no float rounding, no key-name heuristics). A difference is
excused only when its JSON-pointer path matches an entry of the explicit per-artifact
allowlist (replay_allowlist.yaml): `*` matches exactly one path segment. Everything else is an
unexplained difference. The launcher emits artifact_comparison_pass only for
compared artifacts; it cannot certify a complete replay output inventory.

    python3 -I replay_strict.py discover WORKTREE EVIDENCE_ID...   all diffs, no allowlist
    python3 -I replay_strict.py run      WORKTREE EVIDENCE_ID...   verdict with the allowlist
"""
from __future__ import annotations
import json, math, os, re, shlex, subprocess, sys
from pathlib import Path
import yaml

CASE = Path(__file__).resolve().parents[1]
REPO = CASE.parents[2]
PAIRS = CASE / "shards" / "replay_strict_pairs_v2"  # v1 (basename paths) collided for EV-MONO-d90e9c; kept as written


def diff(a, b, p=""):
    """Every differing leaf as (pointer, old, new). Exact comparison."""
    out = []
    if type(a) is not type(b):
        # bool is not int; int vs float is a difference
        out.append((p or "/", a, b))
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b), key=str):
            escaped = str(k).replace("~", "~0").replace("/", "~1")
            q = f"{p}/{escaped}"
            if k not in a:
                out.append((q, "<absent>", b[k]))
            elif k not in b:
                out.append((q, a[k], "<absent>"))
            else:
                out += diff(a[k], b[k], q)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((p + "[len]", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{p}/{i}")
    elif a != b:
        out.append((p or "/", a, b))
    elif isinstance(a, float) and repr(a) != repr(b):
        out.append((p or "/", a, b))
    return out


def allowed(pointer: str, patterns) -> bool:
    segs = pointer[1:].split("/")
    for pat in patterns:
        ps = pat[1:].split("/") if pat.startswith("/") else []
        if len(ps) == len(segs) and all(x == "*" or x == y for x, y in zip(ps, segs)):
            return True
    return False


def metadata_leaf(value, pointer):
    """Resolve a JSON pointer only to an existing scalar metadata leaf."""
    if not pointer or not pointer.startswith("/"):
        return False
    for encoded in pointer[1:].split("/"):
        part = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and part in value:
            value = value[part]
        elif isinstance(value, list) and part.isdecimal() and str(int(part)) == part:
            if int(part) >= len(value):
                return False
            value = value[int(part)]
        else:
            return False
    return not isinstance(value, (dict, list))


def validate_values(value):
    if isinstance(value, dict):
        if any(type(key) is not str for key in value):
            raise ValueError("Result object keys must be strings")
        for child in value.values():
            validate_values(child)
    elif isinstance(value, list):
        for child in value:
            validate_values(child)
    elif type(value) is float and not math.isfinite(value):
        raise ValueError("Nonfinite result number")
    elif type(value) not in (str, int, float, bool, type(None)):
        raise ValueError("Unsupported result value")


def compare(old, new, patterns):
    validate_values(old)
    validate_values(new)
    d = diff(old, new)
    bad = [x for x in d if not (allowed(x[0], patterns)
                               and metadata_leaf(old, x[0])
                               and metadata_leaf(new, x[0]))]
    return d, bad


def load_any(text: str, name: str):
    return json.loads(text) if name.endswith(".json") else yaml.safe_load(text)


def run_one(wt, eid, rows, allow, discover):
    r = rows[eid]
    res = {"evidence_id": eid, "command_file": r["replay_command_file"]}
    cmdf = REPO / r["replay_command_file"]
    lines = [ln for ln in cmdf.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    if len(lines) != 1:
        return {**res, "status": "unknown", "reason": f"{len(lines)} command lines"}
    argv = shlex.split(lines[0])
    if argv[0].startswith("python"):
        argv[0] = "python3"
    subprocess.run(["git", "-C", wt, "checkout", "-q", "--", "."])
    subprocess.run(["git", "-C", wt, "clean", "-fdq"])
    env = {"PATH": os.environ["PATH"], "HOME": wt, "PYTHONHASHSEED": "0"}
    try:
        p = subprocess.run(argv, cwd=wt, env=env, capture_output=True, text=True, timeout=150)
    except subprocess.TimeoutExpired:
        return {**res, "status": "unknown", "reason": "timeout"}
    if p.returncode != 0:
        return {**res, "status": "unknown", "reason": f"exit {p.returncode}"}
    st = subprocess.run(["git", "-C", wt, "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()
    changed = [ln[3:] for ln in st if ln.startswith(" M")]
    files, notcmp = {}, []
    for f in changed:
        if not f.endswith((".json", ".yaml", ".yml")):
            notcmp.append(f)
            continue
        old = subprocess.run(["git", "-C", wt, "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
        newt = (Path(wt) / f).read_text()
        try:
            o, n = load_any(old, f), load_any(newt, f)
        except Exception:
            notcmp.append(f)
            continue
        pats = allow.get(f, [])
        d, bad = compare(o, n, pats)
        files[f] = {"diffs": len(d), "unexplained": len(bad)}
        if discover:
            files[f]["all"] = [(a, str(b)[:60], str(c)[:60]) for a, b, c in d]
        # retain the pair (committed vs regenerated) so the comparison can be redone
        dst = PAIRS / eid / f  # full repo-relative path: no two artifacts can collide
        dst.parent.mkdir(parents=True, exist_ok=True)
        c_p, r_p = dst.parent / (dst.name + ".committed"), dst.parent / (dst.name + ".regenerated")
        if c_p.exists() or r_p.exists():
            raise SystemExit(f"refusing to overwrite retained pair {dst}")
        c_p.write_text(old)
        r_p.write_text(newt)
        if bad and not discover:
            files[f]["unexplained_sample"] = [(a, str(b)[:60], str(c)[:60]) for a, b, c in bad[:6]]
    head = subprocess.run(["git", "-C", wt, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    res.update(files=files, not_compared=notcmp,
               comparison_scope="modified JSON/YAML artifacts only; expected output inventory not certified",
               execution_certified=False,
               receipt={"worktree_commit": head, "argv": argv, "python": sys.version.split()[0],
                        "ran_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})
    if not files:
        res.update(status="unknown", reason="exit 0 but no comparable committed result file was regenerated")
    elif discover:
        res["status"] = "discovery"
    elif any(v["unexplained"] for v in files.values()):
        res["status"] = "fail"
    else:
        res["status"] = "artifact_comparison_pass"
        res["reason"] = "Compared retained artifacts agree; complete replay is not certified"
    return res


def main():
    mode, wt, ids = sys.argv[1], sys.argv[2], sys.argv[3:]
    rows = {}
    for l in open(CASE / "shards/all.jsonl"):
        d = json.loads(l)
        rows[d["evidence_id"]] = d
    allow = yaml.safe_load(open(CASE / "scripts/replay_allowlist.yaml")) if (CASE / "scripts/replay_allowlist.yaml").exists() else {}
    for eid in ids:
        print(json.dumps(run_one(wt, eid, rows, allow or {}, mode == "discover")), flush=True)


if __name__ == "__main__":
    main()

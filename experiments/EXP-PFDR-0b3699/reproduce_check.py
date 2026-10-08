"""EXP-PFDR-0b3699 G-REPRO comparator (TASK-20261002-8a6b8a).  Standard library only.

    <PY> experiments/EXP-PFDR-0b3699/reproduce_check.py \
        --pair ARCHIVED_JOB_DIR NEW_JOB_DIR base \
        --pair ARCHIVED_JOB_DIR EXT_JOB_DIR extended ... --out REPORT.json

For each pair it compares, after gzip decompression and JSON parse, the census rows
(rows.jsonl.gz), harvest rows (harvest-rows.jsonl.gz) and staircase rows
(staircase.jsonl.gz) of the archived EXP-PFDR-011cd0 job with those of the new job:

* census rows keyed by (bits, curve, arm, mode); every key equal except the excluded
  timing / resource-measurement keys (seconds, harvest.harvest_seconds,
  harvest.worker_maxrss_bytes; implementation-notes PDI-2), whose agreement is reported for
  information only;
* harvest rows and staircase rows: the ordered list of records of every
  (bits, curve, m, arm, mode) instance, compared record by record, every key;
* "extended" pairs compare only the arms present in the archived job (the pre-existing arms);
  the new job's records of other arms are listed by arm name and instance status only.

The report names every mismatching key and field; it contains no relation count and nothing
is interpreted.  Exit status 0 iff every pair passes.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import gzip
import hashlib
import json
import os
import sys

REPO = "/home/user/crypto-autoresearcher"
DECLARED_IMPORTS = ("argparse", "ast", "datetime", "gzip", "hashlib", "json", "os", "sys")
EXCLUDED_ROW_KEYS = (("seconds",), ("harvest", "harvest_seconds"), ("harvest", "worker_maxrss_bytes"))
FILES = ("rows.jsonl.gz", "harvest-rows.jsonl.gz", "staircase.jsonl.gz")


def absp(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(REPO, p)


def rel(p: str) -> str:
    return os.path.relpath(absp(p), REPO)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: str) -> list:
    with gzip.open(path, "rt") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def strip_excluded(r: dict) -> tuple[dict, dict]:
    """Return (row without excluded keys, {excluded path: value})."""
    r = json.loads(json.dumps(r))
    removed = {}
    for path in EXCLUDED_ROW_KEYS:
        d = r
        for k in path[:-1]:
            d = d.get(k) if isinstance(d, dict) else None
            if d is None:
                break
        if isinstance(d, dict) and path[-1] in d:
            removed[".".join(path)] = d.pop(path[-1])
    return r, removed


def diff_paths(a, b, path: str = "") -> list[str]:
    """Names of the fields where a and b differ (no values)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            p = f"{path}.{k}" if path else str(k)
            if k not in a or k not in b:
                out.append(p + " (present on one side only)")
            else:
                out.extend(diff_paths(a[k], b[k], p))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [path + " (list length)"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(diff_paths(x, y, f"{path}[{i}]"))
        return out
    return [] if a == b else [path or "<record>"]


def m_of(r: dict):
    if r.get("m") is not None:
        return r["m"]
    meth = str(r.get("method", ""))
    return int(meth[4:]) if meth.startswith("ic_m") else None


def census_key(r: dict) -> str:
    return json.dumps([r.get("bits"), r.get("curve"), m_of(r), r.get("arm"), r.get("mode")])


def group_by_instance(recs: list) -> dict:
    out: dict = {}
    for r in recs:
        out.setdefault(census_key(r), []).append(r)
    return out


def compare_pair(old_dir: str, new_dir: str, kind: str) -> dict:
    od, nd = absp(old_dir), absp(new_dir)
    old = {f: read_jsonl(os.path.join(od, f)) for f in FILES}
    new = {f: read_jsonl(os.path.join(nd, f)) for f in FILES}
    arms_old = sorted({r.get("arm") for r in old["rows.jsonl.gz"]})
    other_arms = sorted({r.get("arm") for r in new["rows.jsonl.gz"]} - set(arms_old))
    if kind == "extended":
        new_cmp = {f: [r for r in recs if r.get("arm") in arms_old] for f, recs in new.items()}
    else:
        new_cmp = new
    mismatches = []
    excluded_info = {".".join(p): {"compared": 0, "equal": 0} for p in EXCLUDED_ROW_KEYS}
    # census rows
    o_rows, n_rows = {}, {}
    for src, dst in ((old["rows.jsonl.gz"], o_rows), (new_cmp["rows.jsonl.gz"], n_rows)):
        for r in src:
            k = census_key(r)
            if k in dst:
                mismatches.append({"file": "rows.jsonl.gz", "key": json.loads(k),
                                   "field": "duplicate key"})
            dst[k] = r
    for k in sorted(set(o_rows) | set(n_rows)):
        if k not in o_rows or k not in n_rows:
            mismatches.append({"file": "rows.jsonl.gz", "key": json.loads(k),
                               "field": "key present on one side only"})
            continue
        a, ra = strip_excluded(o_rows[k])
        b, rb = strip_excluded(n_rows[k])
        for f in diff_paths(a, b):
            mismatches.append({"file": "rows.jsonl.gz", "key": json.loads(k), "field": f})
        for p in excluded_info:
            if p in ra or p in rb:
                excluded_info[p]["compared"] += 1
                excluded_info[p]["equal"] += int(ra.get(p) == rb.get(p))
    # harvest rows and staircases: ordered per instance
    for f in ("harvest-rows.jsonl.gz", "staircase.jsonl.gz"):
        go, gn = group_by_instance(old[f]), group_by_instance(new_cmp[f])
        for k in sorted(set(go) | set(gn)):
            lo, ln = go.get(k, []), gn.get(k, [])
            if len(lo) != len(ln):
                mismatches.append({"file": f, "key": json.loads(k), "field": "record list length"})
                continue
            for i, (x, y) in enumerate(zip(lo, ln)):
                for fld in diff_paths(x, y):
                    mismatches.append({"file": f, "key": json.loads(k), "record_index": i,
                                       "field": fld})
    status_other = {}
    for r in new["rows.jsonl.gz"]:
        if r.get("arm") in other_arms:
            kk = f"{r.get('arm')}|{r.get('status')}"
            status_other[kk] = status_other.get(kk, 0) + 1
    return {"kind": kind, "archived_dir": rel(od), "new_dir": rel(nd),
            "pass": not mismatches,
            "instances_compared": len(o_rows),
            "arms_compared": arms_old,
            "other_arms_in_new_job": other_arms,
            "other_arms_instance_status": status_other,
            "mismatch_count": len(mismatches), "mismatches": mismatches[:2000],
            "excluded_keys": [".".join(p) for p in EXCLUDED_ROW_KEYS],
            "excluded_keys_agreement_information_only": excluded_info,
            "files_sha256": {"archived": {f: sha256(os.path.join(od, f)) for f in FILES},
                             "new": {f: sha256(os.path.join(nd, f)) for f in FILES}}}


def own_imports() -> list[str]:
    tree = ast.parse(open(__file__).read())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mods.add((node.module or "").split(".")[0])
    mods.discard("__future__")
    return sorted(mods)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pair", nargs=3, action="append", required=True,
                    metavar=("ARCHIVED_DIR", "NEW_DIR", "KIND"))
    ap.add_argument("--gate", default="G-REPRO")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        print(f"refusing: {a.out} exists (records are immutable)", file=sys.stderr)
        return 3
    pairs = []
    for old, new, kind in a.pair:
        if kind not in ("base", "extended"):
            print(f"unknown kind {kind}", file=sys.stderr)
            return 2
        pairs.append(compare_pair(old, new, kind))
    imports = own_imports()
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    imports_ok = set(imports) <= set(DECLARED_IMPORTS) and (not stdlib or set(imports) <= stdlib)
    ok = all(p["pass"] for p in pairs) and imports_ok
    rep = {"gate": a.gate, "pass": ok, "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "comparator": "experiments/EXP-PFDR-0b3699/reproduce_check.py",
           "comparator_sha256": sha256(__file__), "imports": imports,
           "imports_subset_of_declared_and_stdlib": imports_ok,
           "rule": ("census rows: every key equal except the excluded timing/resource keys; "
                    "harvest and staircase rows: every record of every instance equal, in order; "
                    "extended pairs: pre-existing arms only"),
           "pairs": pairs}
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({"gate": a.gate, "pass": ok,
                      "pairs": [{"kind": p["kind"], "new_dir": p["new_dir"], "pass": p["pass"],
                                 "mismatch_count": p["mismatch_count"]} for p in pairs]}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

"""EXP-PFDR-1b78f7 regression comparison (gates G1 and G2).

    python3 experiments/EXP-PFDR-1b78f7/compare_regression.py \
        --committed <results/sweep-*.jsonl.gz> --new <run>/rows.jsonl \
        --out <run>/regression-report.json [--la-pivot-flag min_index|min_fill]

Rows are keyed by (bits, curve, method, fb, engine or "enumerate").  Every key
present in the committed row except ``seconds`` is compared for exact equality
after JSON parse.  The new file must hold exactly the committed row count and no
duplicate key.  The committed la_pivot of a row lacking the field is min_index
(README "Pivot rule"); if it differs from the command's --la-pivot flag the
recorded value governs and the difference is reported.  Keys present only in
the new rows (e.g. ``harvest`` under --harvest census, ``engine`` or the table
columns on rows written before those fields existed) are listed, never compared.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter


def key(r: dict) -> tuple:
    return (r["bits"], r["curve"], r["method"], r["fb"], r.get("engine", "enumerate"))


def load(path: str) -> tuple[list[dict], str]:
    raw = open(path, "rb").read()
    text = gzip.decompress(raw).decode() if path.endswith(".gz") else raw.decode()
    return [json.loads(l) for l in text.splitlines() if l.strip()], hashlib.sha256(raw).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--committed", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--la-pivot-flag", default=None,
                    help="the --la-pivot of the regression command (for the pivot report)")
    ap.add_argument("--gate", default="G1")
    a = ap.parse_args(argv)
    com, com_sha = load(a.committed)
    new, new_sha = load(a.new)
    ck = Counter(key(r) for r in com)
    nk = Counter(key(r) for r in new)
    dup_com = sorted([list(k) for k, v in ck.items() if v > 1])
    dup_new = sorted([list(k) for k, v in nk.items() if v > 1])
    newmap = {key(r): r for r in new}
    missing, mismatches, compared_rows, compared_fields = [], [], 0, 0
    extra_keys: Counter = Counter()
    pivot_notes: Counter = Counter()
    for r in com:
        k = key(r)
        q = newmap.get(k)
        if q is None:
            missing.append(list(k))
            continue
        compared_rows += 1
        for f in r:
            if f == "seconds":
                continue
            compared_fields += 1
            if f not in q or q[f] != r[f]:
                mismatches.append({"key": list(k), "field": f, "committed": r[f],
                                   "new": q.get(f, "<absent>")})
        for f in q:
            if f not in r:
                extra_keys[f] += 1
        if r["method"] != "rho":
            eff = r.get("la_pivot", "min_index")
            pivot_notes[f"committed={eff}|new={q.get('la_pivot')}|flag={a.la_pivot_flag}"] += 1
    extra_rows = sorted([list(k) for k in nk if k not in ck])
    ok = (not missing and not mismatches and not dup_new and not extra_rows
          and len(new) == len(com) and compared_rows == len(com))
    rep = {
        "gate": a.gate, "pass": ok,
        "committed_file": a.committed, "committed_sha256": com_sha, "committed_rows": len(com),
        "new_file": a.new, "new_sha256_uncompressed": new_sha, "new_rows": len(new),
        "row_count_equal": len(new) == len(com),
        "rows_compared": compared_rows,
        "fraction_committed_rows_compared": compared_rows / len(com) if com else None,
        "fields_compared": compared_fields,
        "missing_in_new": missing, "extra_rows_in_new": extra_rows,
        "duplicate_keys_committed": dup_com, "duplicate_keys_new": dup_new,
        "mismatches": mismatches[:500], "mismatch_count": len(mismatches),
        "mismatch_fields": dict(Counter(m["field"] for m in mismatches)),
        "keys_only_in_new_rows": dict(extra_keys),
        "la_pivot_report": dict(pivot_notes),
        "excluded_field": "seconds",
        "key": ["bits", "curve", "method", "fb", "engine (absent = enumerate)"],
    }
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=2, sort_keys=True)
    print(json.dumps({k: rep[k] for k in ("gate", "pass", "committed_rows", "new_rows",
                                          "rows_compared", "mismatch_count", "la_pivot_report")},
                     indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

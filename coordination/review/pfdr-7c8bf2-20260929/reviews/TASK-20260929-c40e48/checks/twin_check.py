#!/usr/bin/env python3
"""TASK-20260929-c40e48 (validator), joint J1: independent P1 twin check of
EXP-PFDR-7c8bf2 from the committed input files only (specification P1 text).

For every mitm row of each min_index twin, find the min_fill row with the same
(bits, curve, method, fb, engine) and compare the twelve listed fields. Also
checks the reverse direction, field presence (so no row is skipped silently for
lacking a field), duplicate keys, and reports which OTHER fields differ.
"""
import collections
import gzip
import json
import sys

FIELDS = ["p", "a", "b", "N", "fb_size", "s3_solves", "table_s3_solves", "table_entries",
          "relations", "attempts", "rank", "target_ops"]
PAIRS = [("sweep-mitm-20260926", "sweep-minfill-20260926"),
         ("sweep-arity-20260926", "sweep-arity-minfill-20260926")]


def load(d, f):
    with gzip.open(f"{d}/{f}.jsonl.gz", "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def key(r):
    return (r["bits"], r["curve"], r["method"], r["fb"], r.get("engine"))


def main(d):
    report = {}
    for twin, prim in PAIRS:
        T = [r for r in load(d, twin) if r["method"].startswith("ic_") and r.get("engine") == "mitm"]
        P = [r for r in load(d, prim) if r["method"].startswith("ic_") and r.get("engine") == "mitm"]
        tk = collections.Counter(key(r) for r in T)
        pk = collections.Counter(key(r) for r in P)
        pidx = {key(r): r for r in P}
        missing, mismatches, absent_fields = [], [], []
        other_diff = collections.Counter()
        compared = 0
        for r in T:
            q = pidx.get(key(r))
            if q is None:
                missing.append(key(r))
                continue
            for fld in FIELDS:
                if fld not in r or fld not in q:
                    absent_fields.append((key(r), fld))
                elif r[fld] != q[fld]:
                    mismatches.append({"key": key(r), "field": fld, "twin": r[fld], "primary": q[fld]})
            compared += 1
            for fld in set(r) | set(q):
                if fld not in FIELDS and r.get(fld) != q.get(fld):
                    other_diff[fld] += 1
        report[f"{twin} -> {prim}"] = {
            "twin_mitm_rows": len(T), "primary_mitm_rows": len(P), "pairs_compared": compared,
            "fields_compared_per_pair": len(FIELDS), "field_comparisons": compared * len(FIELDS),
            "missing_twin": missing, "mismatches": mismatches, "absent_fields": absent_fields,
            "primary_rows_without_twin": sorted(set(pk) - set(tk)),
            "duplicate_keys_twin": [k for k, v in tk.items() if v > 1],
            "duplicate_keys_primary": [k for k, v in pk.items() if v > 1],
            "other_fields_that_differ_count": dict(sorted(other_diff.items())),
        }
    ok = all(not v["missing_twin"] and not v["mismatches"] and not v["absent_fields"]
             for v in report.values())
    print(json.dumps({"P1_holds": ok, "detail": report}, indent=1, default=list))


if __name__ == "__main__":
    main(sys.argv[1])

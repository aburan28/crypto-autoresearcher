"""J-A3 (2)/(3) comparator, TASK-20261009-33b5cf. Own implementation (standard library
only; reproduce_check.py is NOT imported or run).

Sources per job (4-b30-c10, 4-b32-c10):
  ARCH  experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-table/attempt-1/jobs/<job>/
  R1    <scratch>/j-a3/<job>/run1/   (38be58dad bytes, review computation)
  R2    <scratch>/j-a3/<job>/run2/   (38be58dad bytes, review computation)
  EC    experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-repro/attempt-1/jobs/<job>/
        (RA-02, EC-A1 build; base-arm job, for the (3) attribution)

Census rows (rows.jsonl.gz) are matched by (bits, curve, m, arm, mode), the A-3 key.
Every row is flattened to dot-paths (nested dicts; lists and scalars are leaf values).
Per pair: for each of the three A-3-excluded keys, the number of matched rows on which
the key is equal; for every other key, the number of matched rows on which it differs
(presence counts: a key present in one row and absent in the other is a difference).
Harvest rows and staircase rows are compared record by record in file order (whole
record equality after JSON parse) and as decompressed bytes. bases.jsonl.gz is also
compared as decompressed bytes (informational; not in G-REPRO).
No seeds (deterministic comparison).
Usage: python compare_ja3.py <repo> <scratch> <out.json>
"""
import gzip
import json
import os
import sys
from itertools import combinations

EXCL = ("seconds", "harvest.harvest_seconds", "harvest.worker_maxrss_bytes")
KEY = ("bits", "curve", "m", "arm", "mode")


def flat(d, pre=""):
    out = {}
    for k, v in d.items():
        p = f"{pre}{k}"
        if isinstance(v, dict):
            out.update(flat(v, p + "."))
        else:
            out[p] = v
    return out


def load_lines(path):
    with gzip.open(path, "rt") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def raw(path):
    with gzip.open(path, "rb") as fh:
        return fh.read()


def census(path):
    rows = load_lines(path)
    m = {}
    dup = 0
    for r in rows:
        k = tuple(r.get(x) for x in KEY)
        if k in m:
            dup += 1
        m[k] = flat(r)
    return m, len(rows), dup


def cmp_census(a, b):
    ka, kb = set(a), set(b)
    common = sorted(ka & kb, key=str)
    res = {"rows_a": len(a), "rows_b": len(b), "matched": len(common),
           "only_a": len(ka - kb), "only_b": len(kb - ka),
           "excluded_key_rows_equal": {}, "excluded_key_rows_present_both": {},
           "other_key_rows_differing": {}, "other_keys_compared": 0}
    for e in EXCL:
        both = [k for k in common if e in a[k] and e in b[k]]
        res["excluded_key_rows_present_both"][e] = len(both)
        res["excluded_key_rows_equal"][e] = sum(1 for k in both if a[k][e] == b[k][e])
    keys = set()
    for k in common:
        keys |= set(a[k]) | set(b[k])
    others = sorted(keys - set(EXCL))
    res["other_keys_compared"] = len(others)
    for key in others:
        n = sum(1 for k in common if (key in a[k]) != (key in b[k]) or a[k].get(key) != b[k].get(key))
        if n:
            res["other_key_rows_differing"][key] = n
    res["rows_differing_on_any_non_excluded_key"] = sum(
        1 for k in common if any((key in a[k]) != (key in b[k]) or a[k].get(key) != b[k].get(key)
                                 for key in others))
    return res


def cmp_seq(pa, pb):
    la, lb = load_lines(pa), load_lines(pb)
    n = min(len(la), len(lb))
    diff = sum(1 for i in range(n) if la[i] != lb[i])
    return {"records_a": len(la), "records_b": len(lb), "records_differing_in_file_order": diff,
            "decompressed_bytes_identical": raw(pa) == raw(pb)}


def maxrss_profile(m):
    vals = [r.get("harvest.worker_maxrss_bytes") for r in m.values()]
    vals = [v for v in vals if v is not None]
    return {"rows_with_key": len(vals), "distinct_values": len(set(vals)),
            "min": min(vals) if vals else None, "max": max(vals) if vals else None}


def main():
    repo, scratch, out = sys.argv[1], sys.argv[2], sys.argv[3]
    report = {"excluded_keys": list(EXCL), "match_key": list(KEY), "jobs": {}}
    for job in ("4-b30-c10", "4-b32-c10"):
        src = {
            "ARCH": os.path.join(repo, "experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-table/attempt-1/jobs", job),
            "R1": os.path.join(scratch, "j-a3", job, "run1"),
            "R2": os.path.join(scratch, "j-a3", job, "run2"),
            "EC": os.path.join(repo, "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-repro/attempt-1/jobs", job),
        }
        cen = {}
        jr = {"sources": src, "census_rows": {}, "maxrss_profile": {}, "pairs": {}}
        for s, d in src.items():
            m, n, dup = census(os.path.join(d, "rows.jsonl.gz"))
            cen[s] = m
            jr["census_rows"][s] = {"lines": n, "duplicate_keys": dup}
            jr["maxrss_profile"][s] = maxrss_profile(m)
        for a, b in [("ARCH", "R1"), ("ARCH", "R2"), ("R1", "R2"), ("ARCH", "EC"), ("EC", "R1"), ("EC", "R2")]:
            pr = {"census": cmp_census(cen[a], cen[b])}
            for f in ("harvest-rows.jsonl.gz", "staircase.jsonl.gz", "bases.jsonl.gz"):
                pr[f] = cmp_seq(os.path.join(src[a], f), os.path.join(src[b], f))
            jr["pairs"][f"{a}_vs_{b}"] = pr
        report["jobs"][job] = jr
    json.dump(report, open(out, "w"), indent=1)
    for job, jr in report["jobs"].items():
        print("==", job, jr["census_rows"], jr["maxrss_profile"])
        for p, pr in jr["pairs"].items():
            c = pr["census"]
            print(f"  {p}: matched {c['matched']} onlyA {c['only_a']} onlyB {c['only_b']} "
                  f"excl_equal {c['excluded_key_rows_equal']} of {c['excluded_key_rows_present_both']} "
                  f"| other keys {c['other_keys_compared']} differing {c['other_key_rows_differing']} "
                  f"rows_diff_nonexcl {c['rows_differing_on_any_non_excluded_key']} "
                  f"| harvest {pr['harvest-rows.jsonl.gz']} | stair {pr['staircase.jsonl.gz']} "
                  f"| bases_bytes_identical {pr['bases.jsonl.gz']['decompressed_bytes_identical']}")


if __name__ == "__main__":
    main()

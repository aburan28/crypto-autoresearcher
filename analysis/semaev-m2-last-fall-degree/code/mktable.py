#!/usr/bin/env python3
"""Summarize results/cache/*.json into results/summary.md (per (family, n) rows)."""
import json, glob, collections
recs = [json.load(open(f)) for f in sorted(glob.glob("results/cache/*.json"))]
rows = collections.OrderedDict()
fam = {"poly": "polynomial", "rand": "random", "tr0": "random in ker Tr"}
for r in sorted(recs, key=lambda r: ({"P": 0, "R": 1, "U": 2, "T": 3, "S": 4}[r["name"][0]], r["n"], r["name"])):
    key = (r["name"][0], fam[r["basis"]], r["zmode"], r["n"], r["k"])
    rows.setdefault(key, []).append(r)
out = ["| family | z | n | k | instances | W_2 refutes | W_3 refutes | W_4 refutes | d_LFD (exact unless marked) |", "|---|---|---|---|---|---|---|---|---|"]
for (p, b, zm, n, k), rs in rows.items():
    def cnt(D):
        tested = [r for r in rs if str(D) in r["closures"] or any(int(e) < D and r["closures"][e].get("W_one") for e in r["closures"])]
        yes = [r for r in rs if any(int(e) <= D and r["closures"][e].get("W_one") for e in r["closures"])]
        untested = [r for r in rs if str(D) not in r["closures"] and not any(int(e) < D and r["closures"][e].get("W_one") for e in r["closures"])]
        return f"{len(yes)}/{len(rs)}" + (f" ({len(untested)} untested)" if untested else "")
    ds = []
    for r in rs:
        if r.get("d_ref_exact") is not None: ds.append(str(r["d_ref_exact"]))
        elif r.get("d_ref_lower_bound") is not None: ds.append(f"≥{r['d_ref_lower_bound']}")
        else: ds.append("?")
    c = collections.Counter(ds)
    out.append(f"| {p}: {b} | {zm} | {n} | {k} | {len(rs)} | {cnt(2)} | {cnt(3)} | {cnt(4)} | " + ", ".join(f"{v}×{d}" for d, v in sorted(c.items())) + " |")
open("results/summary.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))

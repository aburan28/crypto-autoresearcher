#!/usr/bin/env python3
"""Added AFTER the analyze.py replay: robustness variants of the frozen-criteria derivation.
 (a) planted-only reading (random targets at every L,m=4 give a trivial basis [1] = no decomposition),
 (b) per-instance paired lower bounds at L=4 (A_elim censored at >= its timeout wall),
 (c) cap what-if for the planted-only reading.  Imports derive_criteria.py unchanged."""
import json, statistics, sys
sys.path.insert(0, "/tmp/claude-0/validator4")
import derive_criteria as dc
cells, runs = dc.build_map()
kind = {}
for r in (1, 2, 3, 4):
    for x in runs[r]:
        kind[(x["L"], x["inst"])] = x["kind"]
def only(cells, k):
    return {L: {a: [r for r in rows if kind[(L, r[0])] == k] for a, rows in d.items()} for L, d in cells.items()}
P = only(cells, "planted")
print("== planted-only medians (all non-degenerate planted instances) ==")
for L in sorted(P):
    for arm in dc.ARMS:
        s = dc.stats(P[L][arm]); print(f"L={L} {arm:11s} nd={s['n_nd']} ok={s['n_ok']} to={s['n_timeout']} median={s['median']} walls={s['walls']}")
v = dc.verdict(P)
print("planted-only verdict:", json.dumps({k: {kk: vv for kk, vv in v[k].items() if kk in ('joint', 'success', 'falsif_clause1', 'falsif_clause2', 'falsification', 'retired_L', 'largest_completed_L')} for k in ('msolve', 'singular')}, default=str))
print("planted-only dynamic range:", v["dynamic_range"])
print("planted-only cap what-if (B_ms retired at L=4 when cap < min planted completion):")
for cap in (600, 590, 586.3, 586, 584, 583.3, 583.1, 583.0, 582.9, 560):
    vv = dc.verdict(P, cap=cap)
    print(f"  cap={cap}: B_ms retired L={vv['msolve']['retired_L'][1]} A_elim retired L={vv['msolve']['retired_L'][0]} clause1={vv['msolve']['falsif_clause1']} clause2={vv['msolve']['falsif_clause2']}")
print("== L=4 per-instance lower bound on A_elim_ms/B_ms (A_elim censored at its timeout wall) ==")
a = {r[0]: r[2] for r in cells[4]["A_elim_ms"] if r[1] == "timeout"}
b = {r[0]: r[2] for r in cells[4]["B_ms"] if r[1] == "ok"}
lbs = {i: round(a[i] / b[i], 3) for i in sorted(set(a) & set(b))}
print(lbs, " median lower bound:", round(statistics.median(lbs.values()), 3))
print("A_elim L=3 -> L=4 growth needed to finish within 600 s: <=", round(600 / 12.9294, 1), "x ; B_ms L=3->L=4 growth observed:", round(582.9961 / 10.7005, 1), "x (medians; informational)")
print("random-target instances: B_ms basis is [1] (gb_size=1) at every L, see raw rows; planted B_ms bases have 15 elements at L=4")

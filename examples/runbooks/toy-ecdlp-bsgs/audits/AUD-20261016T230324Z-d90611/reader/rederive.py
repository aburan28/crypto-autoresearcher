"""Reader half of audit-runs for RBS-EXAMPLE-b301f5 (written blind of solve.py/check.py).

1. Blind re-derivation: recompute the runbook's metrics (group_ops, giant_steps,
   solved_fraction) over the twelve search trials from each unit's raw-result.json,
   using only their definitions in runbook.yaml.
2. Certificates: verify k*G = Q with affine double-and-add written here (shares no
   code with solve.py or check.py), for two replayed and two unreplayed units, and
   check both controls.
Usage: python3 -I rederive.py <session_dir> <curve.json>
"""
import json, statistics, sys
from pathlib import Path

session, curve = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text())
p, a, b, n, G = curve["p"], curve["a"], curve["b"], curve["n"], tuple(curve["G"])

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    if P == Q: l = (3 * P[0] * P[0] + a) * pow(2 * P[1], p - 2, p) % p
    else: l = (Q[1] - P[1]) * pow(Q[0] - P[0], p - 2, p) % p
    x = (l * l - P[0] - Q[0]) % p
    return (x, (l * (P[0] - x) - P[1]) % p)

def mul(k, P):
    R = None
    while k:
        if k & 1: R = add(R, P)
        P, k = add(P, P), k >> 1
    return R

on_curve = lambda P: (P[1] ** 2 - P[0] ** 3 - a * P[0] - b) % p == 0
units = {}
for u in sorted((session / "units").iterdir()):
    r = json.loads((u / "raw-result.json").read_text())
    units[r["trial_id"]] = (u.name, r)

search = [r for _, r in units.values() if r["mode"] == "search"]
ops = [r["group_ops"] for r in search]
gs = [r["giant_steps"] for r in search]
print(json.dumps({"metrics": {
    "group_ops": {"count": len(ops), "mean": statistics.mean(ops), "median": statistics.median(ops), "min": min(ops), "max": max(ops)},
    "giant_steps": {"mean": statistics.mean(gs), "min": min(gs), "max": max(gs)},
    "solved_fraction": {"count": len(search), "fraction_true": sum(r["verified"] is True for r in search) / len(search)},
}}, sort_keys=True))
assert mul(n, G) is None and on_curve(G)
m = 1024
for tid in sys.argv[3:]:
    run, r = units[tid]
    Q = tuple(r["Q"])
    if r["mode"] == "off-curve":
        print(tid, run, "Q on curve:", on_curve(Q), "status:", r["status"], "k_found:", r["k_found"])
        continue
    k = r["k_found"]
    print(tid, run, "k*G == Q:", mul(k, G) == Q, "giant_steps == k//m+1:", r["giant_steps"] == k // m + 1)

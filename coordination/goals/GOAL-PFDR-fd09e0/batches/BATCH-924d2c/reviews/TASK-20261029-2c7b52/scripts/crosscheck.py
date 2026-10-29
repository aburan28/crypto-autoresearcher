# Second, separately written path for the load-bearing per-cell numbers (statistics module on
# Fractions, float sqrt, sorted-float bootstrap) compared with out/outputs/blind-cells.json.
import json, os, sys, statistics, random, hashlib, math
from fractions import Fraction as Fr
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cells = {c["cell"]: c for c in json.load(open(os.path.join(ROOT, "out/outputs/blind-cells.json")))["cells"]}
seeds = json.load(open(os.path.join(ROOT, "out/outputs/bootstrap-seed.json")))["seeds"]
recs = [json.loads(l) for l in open(os.path.join(ROOT, "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl"))]
groups = {}
for r in recs:
    if r["status"] == "ok":
        groups.setdefault(r["cell"], []).append(r)
worst = {}
mism = []
for cell, rs in groups.items():
    rs.sort(key=lambda r: r["c"])
    S = sum(r["gap_C"] for r in rs)
    M = sum(statistics.mean([Fr(x) for x in r["null_C"]]) for r in rs)
    V = sum(statistics.variance([Fr(x) for x in r["null_C"]]) for r in rs)
    Sp = sum(r["plant_C"] for r in rs)
    z = float(S - M) / math.sqrt(float(V) * 1.05)
    pz = float(Sp - M) / math.sqrt(float(V) * 1.05)
    S0 = sum(r["null_C"][0] for r in rs)
    M19 = sum(statistics.mean([Fr(x) for x in r["null_C"][1:]]) for r in rs)
    V19 = sum(statistics.variance([Fr(x) for x in r["null_C"][1:]]) for r in rs)
    zc = float(S0 - M19) / math.sqrt(float(V19) * 20 / 19)
    c = cells[cell]
    checks = {"S": (S, c["S"]), "M": (str(M) if M.denominator != 1 else str(M.numerator), c["M_exact"]),
              "V": (str(V) if V.denominator != 1 else str(V.numerator), c["V_exact"]),
              "kappa": (Fr(S) / M == Fr(c["kappa_exact"]), True)}
    for k, (a, b) in checks.items():
        if a != b:
            mism.append((cell, k, a, b))
    for k, a, b in (("z", z, c["z"]), ("plant_z", pz, c["plant_z"]), ("z_cal", zc, c["z_cal"])):
        rel = abs(a - b) / max(1e-12, abs(b))
        worst[k] = max(worst.get(k, 0), rel)
    # bootstrap, family A, nearest rank via floats
    rng = random.Random(seeds[cell]["A"])
    k = len(rs)
    g = [r["gap_C"] for r in rs]
    m = [sum(r["null_C"]) / 20 for r in rs]
    vals = []
    for _ in range(2000):
        idx = [rng.randrange(k) for _ in range(k)]
        vals.append(sum(g[i] for i in idx) / sum(m[i] for i in idx))
    vals.sort()
    lo, hi = vals[49], vals[1949]
    a, b = c["bootstrap"]["A"]["kappa_ci95_nearest_rank"]
    worst["ci"] = max(worst.get("ci", 0), abs(lo - a), abs(hi - b))
print("python", sys.version.split()[0])
print("exact mismatches:", mism)
print("max relative diff (z, plant_z, z_cal) and max abs diff (bootstrap nearest-rank edges):", worst)

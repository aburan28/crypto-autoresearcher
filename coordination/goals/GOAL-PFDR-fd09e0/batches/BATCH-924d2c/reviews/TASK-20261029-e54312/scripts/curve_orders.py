"""J2b(3): independent certification of #E(F_p) = N on 10 sampled curves per bits.

Curves: outputs/recount-selection.json curve_order_sample (fixed with the job sample, before any order was
checked). Curve parameters regenerated from seed 8,100,000 + c by scripts/ownec.py and compared with the record.
Methods (stated per curve):
  exhaustive : #E = p + 1 + sum_x legendre(x^3 + a x + b), every x in F_p, numpy-vectorised Euler criterion
               (20 bits: all 10 curves; 24 bits: the first 2 curves of the list);
  pari       : PARI/GP ellcard(ellinit([a, b], p)) (every curve);
  certificate: N prime, N > 4 sqrt(p) + 4, (N - p - 1)^2 <= 4p and [N]P = O for 3 random points P != O by
               reviewer Jacobian scalar multiplication; with N prime this forces #E = N (every curve).

usage: python3 -I -B curve_orders.py <recount-selection.json> <scratch-dir> <out.json>
"""
import json
import math
import os
import random
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ownec  # noqa: E402

sel_p, scratch, out_p = sys.argv[1:4]
os.makedirs(scratch, exist_ok=True)
sel = json.load(open(sel_p))
jobs_by_c = {}
recs = {}
for ln in open("experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl"):
    r = json.loads(ln)
    recs.setdefault((r["bits"], r["c"]), (r["p"], r["a"], r["b_coef"], r["N"]))


def powmod_vec(base, e, p):
    res = np.ones_like(base)
    b = base % p
    while e:
        if e & 1:
            res = res * b % p
        b = b * b % p
        e >>= 1
    return res


def exhaustive(p, a, b):
    total = 0
    step = 1 << 21
    for start in range(0, p, step):
        x = np.arange(start, min(p, start + step), dtype=np.int64)
        f = (x * x % p * x % p + a * x % p + b) % p
        leg = powmod_vec(f, (p - 1) // 2, p)
        total += int(np.count_nonzero(leg == 1)) - int(np.count_nonzero(leg == p - 1))
    return p + 1 + total


rows = []
gp_lines = []
for bits in ("20", "24", "28"):
    for i, ent in enumerate(sel["curve_order_sample"][bits]):
        c = ent["c"]
        p, a, b, N, _ = ownec.regenerate_curve(int(bits), ownec.SEED_BLOCK["main"] + c)
        row = {"bits": int(bits), "c": c, "selected_by": ent["source"], "p": p, "a": a, "b": b, "N_recorded": recs[(int(bits), c)][3],
               "curve_equals_record": (p, a, b, N) == recs[(int(bits), c)], "methods": {}}
        Nr = row["N_recorded"]
        if bits == "20" or (bits == "24" and i < 2):
            t0 = time.time()
            Ne = exhaustive(p, a, b)
            row["methods"]["exhaustive"] = {"count": Ne, "equal": Ne == Nr, "seconds": round(time.time() - t0, 2)}
        rng = random.Random(f"TASK-20261029-e54312|J2b|orders|{bits}|{c}")
        E = ownec.EC(p, a, b)
        pts = [E.random_point(rng) for _ in range(3)]
        row["methods"]["certificate"] = {
            "N_prime": ownec.is_prime(Nr), "N_gt_4sqrtp_plus_4": Nr > 4 * math.isqrt(p) + 4,
            "hasse": (Nr - p - 1) ** 2 <= 4 * p, "NP_is_O_for_3_points": all(E.mul(Nr, P) is None for P in pts),
            "points_not_O": all(P is not None for P in pts)}
        row["methods"]["certificate"]["certifies"] = all(row["methods"]["certificate"].values())
        gp_lines.append(f'print({bits}," ",{c}," ",ellcard(ellinit([{a},{b}],{p})));')
        rows.append(row)
gp_in = os.path.join(scratch, "orders.gp")
with open(gp_in, "w") as f:
    f.write("\n".join(gp_lines) + "\nquit;\n")
gp = subprocess.run(["gp", "-q", "-f", gp_in], capture_output=True, text=True, timeout=600)
card = {(int(x.split()[0]), int(x.split()[1])): int(x.split()[2]) for x in gp.stdout.strip().splitlines()}
for row in rows:
    v = card[(row["bits"], row["c"])]
    row["methods"]["pari"] = {"ellcard": v, "equal": v == row["N_recorded"]}
    row["certified"] = row["curve_equals_record"] and all(m.get("equal", m.get("certifies")) for m in row["methods"].values())
out = {"script": "scripts/curve_orders.py", "python": sys.version, "executable": sys.executable,
       "pari": subprocess.run(["gp", "--version-short"], capture_output=True, text=True).stdout.strip(),
       "numpy": np.__version__, "curves": rows,
       "summary": {"curves": len(rows), "certified": sum(r["certified"] for r in rows),
                   "exhaustive_counts": sum("exhaustive" in r["methods"] for r in rows),
                   "per_bits_methods": {b: sorted({k for r in rows if r["bits"] == int(b) for k in r["methods"]}) for b in ("20", "24", "28")}}}
with open(out_p, "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(json.dumps(out["summary"]))

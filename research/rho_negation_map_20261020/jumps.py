#!/usr/bin/env python3
"""Side measurement: does a larger r-adding table close the negation walk's
gap to its floor?  Negation walk at r in {20, 32, 64} on the same instances
(24-32 bits, 8 curves x 16 targets), walk_ops / sqrt(N) / sqrt(pi/4)."""
import json
import math
import random
import statistics
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from crypto_autoresearcher.index_calculus import pollard_rho
from crypto_autoresearcher.index_calculus.curve import (
    generate_prime_order_curve,
)

SEED, RS, BITS = 20261021, (20, 32, 64), (24, 28, 32)

def job(a):
    bits, c = a
    E, P = generate_prime_order_curve(bits, 100 + c)
    rng = random.Random(f"{SEED}|{bits}|{c}")
    out = []
    for t in range(16):
        k = rng.randrange(1, E.order); Q = E.mul(k, P)
        for r in RS:
            rr = pollard_rho(E, P, Q, seed=SEED + 1000 * c + t, r=r)
            assert rr.verified and rr.k == k
            out.append({"bits": bits, "curve": c, "target": t, "r": r,
                        "over_floor": rr.walk_ops / math.sqrt(math.pi * E.order / 4),
                        "setup_ops": rr.setup_ops, "escapes": rr.escapes})
    return out

with Pool() as pool:
    rows = [x for xs in pool.map(job, [(b, c) for b in BITS for c in range(8)]) for x in xs]
summ = {}
for r in RS:
    v = [x["over_floor"] for x in rows if x["r"] == r]
    summ[r] = {"n": len(v), "mean_over_floor": statistics.mean(v),
               "se": statistics.stdev(v) / math.sqrt(len(v)),
               "escapes_per_solve": statistics.mean(x["escapes"] for x in rows if x["r"] == r)}
    print(r, {k: round(w, 4) for k, w in summ[r].items()})
Path("jumps.json").write_text(json.dumps({"seed": SEED, "bits": BITS, "summary": summ, "rows": rows}, indent=1))

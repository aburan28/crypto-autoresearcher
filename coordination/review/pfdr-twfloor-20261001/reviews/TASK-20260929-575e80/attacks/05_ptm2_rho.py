"""05 -- PTM-2: the rho panel under the per-instance predicate (choices PTM-2; MC-6).

Observed: R13 rho rows (110) and the j0-panel rho rows (35). q1 = walk_ops/sqrt(N) (one
encoding per walk step), q2 = walk_ops/(0.5*sqrt(N)) (the two-encodings analogue);
setup_ops excluded (README "How cost is counted"). Fraction below 0.9 under each.

Predictions:
 (a) the plan's negation-folded birthday law P(q <= t) = 1 - exp(-t^2) (x-key collisions):
     q1 < 0.9 -> 1 - exp(-0.81) = 0.555; q2 < 0.9 <=> q1 < 0.45 -> 1 - exp(-0.2025) = 0.183;
 (b) full-point (non-folded) birthday P = 1 - exp(-t^2/2): rho.py keys its table on the
     point X itself (table.get(X)), so X and -X do not collide;
 (c) design-evaluated (MC-6): my own simulation of rho.py's algorithm over Z_N -- r = 20
     adding walk, x-coordinate replaced by a seeded hash of the +-class (step choice x mod 20,
     distinguished test (x // 20) & mask == 0, dp_bits = N.bit_length()//2 - 5, max_len =
     20 << dp_bits, table keyed by the element, merge rule, restarts) -- at one representative
     N per rung (the median census N of the rung), 1000 runs per rung at 12..24 bits and 200
     at 26..32 bits (seeds = run index). Each run is one seed (MC-2): binomial MC s.e. given.
"""
import json
import math
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import CANON, OUT, dump, iter_jsonl  # noqa: E402
from numlib import poisson_binomial_tail  # noqa: E402

MASK64 = (1 << 64) - 1


def splitmix(x):
    x = (x + 0x9E3779B97F4A7C15) & MASK64
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & MASK64
    return x ^ (x >> 31)


def simulate_rho(N, seed, r=20, max_walks=1000):
    """rho.py's walk over Z_N: a position is v = a + b*k; x(v) = hash of the class {v, -v}."""
    rng = random.Random(f"ptm2|{N}|{seed}")
    k = rng.randrange(1, N)
    key = rng.getrandbits(64)
    dp_bits = max(0, N.bit_length() // 2 - 5)
    mask = (1 << dp_bits) - 1
    max_len = 20 << dp_bits
    steps = []
    for _ in range(r):
        c, d = rng.randrange(N), rng.randrange(N)
        steps.append(((c + d * k) % N, c, d))
    table = {}
    walk_ops = 0
    for walk in range(1, max_walks + 1):
        a, b = rng.randrange(N), rng.randrange(N)
        v = (a + b * k) % N
        for _ in range(max_len):
            if v == 0:
                break
            x = splitmix((min(v, N - v) ^ key) & MASK64) % N
            if (x // r) & mask == 0:
                prev = table.get(v)
                if prev is not None:
                    a2, b2 = prev
                    if (b - b2) % N:
                        kk = (a2 - a) * pow(b - b2, -1, N) % N
                        assert kk == k
                        return walk_ops, walk
                    break
                table[v] = (a, b)
            mv, c, d = steps[x % r]
            v = (v + mv) % N
            a, b = (a + c) % N, (b + d) % N
            walk_ops += 1
    return None, max_walks


def main():
    obs = []
    for r in iter_jsonl(CANON["rho"]):
        if r.get("method") == "rho":
            obs.append(("rho", r))
    for r in iter_jsonl(CANON["j0"]):
        if r.get("method") == "rho":
            obs.append(("j0", r))
    rows = []
    for panel, r in obs:
        if r.get("status") != "completed_valid":
            rows.append({"panel": panel, "bits": r["bits"], "curve": r["curve"], "status": r.get("status")})
            continue
        q1 = r["walk_ops"] / math.sqrt(r["N"])
        rows.append({"panel": panel, "bits": r["bits"], "curve": r["curve"], "N": r["N"],
                     "walk_ops": r["walk_ops"], "setup_ops": r["setup_ops"], "walks": r["walks"],
                     "q1": q1, "q2": 2 * q1, "status": "completed_valid"})
    ok = [x for x in rows if x["status"] == "completed_valid"]
    pa1, pa2 = 1 - math.exp(-0.81), 1 - math.exp(-0.2025)
    pb1, pb2 = 1 - math.exp(-0.405), 1 - math.exp(-0.10125)
    # design-evaluated simulation per rung
    sim = {}
    for bits in sorted({x["bits"] for x in ok}):
        Ns = sorted(x["N"] for x in ok if x["bits"] == bits)
        N = Ns[len(Ns) // 2]
        runs = 1000 if bits <= 24 else 200
        qs = []
        fails = 0
        for s in range(runs):
            w, _ = simulate_rho(N, s)
            if w is None:
                fails += 1
                continue
            qs.append(w / math.sqrt(N))
        n = len(qs)
        p1 = sum(q < 0.9 for q in qs) / n
        p2 = sum(q < 0.45 for q in qs) / n
        sim[str(bits)] = {"N": N, "runs": runs, "failed_runs": fails, "median_q1": statistics.median(qs),
                          "mean_q1": statistics.fmean(qs),
                          "p_q1_lt_0.9": p1, "se1": math.sqrt(p1 * (1 - p1) / n),
                          "p_q2_lt_0.9": p2, "se2": math.sqrt(p2 * (1 - p2) / n)}
        print(bits, sim[str(bits)], flush=True)

    def block(sel):
        xs = [x for x in ok if sel(x)]
        n = len(xs)
        f1 = sum(x["q1"] < 0.9 for x in xs)
        f2 = sum(x["q2"] < 0.9 for x in xs)
        pc1 = [sim[str(x["bits"])]["p_q1_lt_0.9"] for x in xs]
        pc2 = [sim[str(x["bits"])]["p_q2_lt_0.9"] for x in xs]
        return {"n": n, "fire_q1": f1, "frac_q1": f1 / n, "fire_q2": f2, "frac_q2": f2 / n,
                "median_q1": statistics.median(x["q1"] for x in xs),
                "pred_a_negfolded": {"q1": pa1, "q2": pa2, "E_q1": pa1 * n, "E_q2": pa2 * n,
                                     "P_le_obs_q1": 1 - poisson_binomial_tail([pa1] * n, f1 + 1),
                                     "P_ge_obs_q1": poisson_binomial_tail([pa1] * n, f1)},
                "pred_b_fullpoint": {"q1": pb1, "q2": pb2, "E_q1": pb1 * n, "E_q2": pb2 * n,
                                     "P_ge_obs_q1": poisson_binomial_tail([pb1] * n, f1),
                                     "P_le_obs_q1": 1 - poisson_binomial_tail([pb1] * n, f1 + 1)},
                "pred_c_design": {"E_q1": sum(pc1), "E_q2": sum(pc2),
                                  "P_ge_obs_q1": poisson_binomial_tail(pc1, f1),
                                  "P_le_obs_q1": 1 - poisson_binomial_tail(pc1, f1 + 1),
                                  "P_ge_obs_q2": poisson_binomial_tail(pc2, f2),
                                  "P_le_obs_q2": 1 - poisson_binomial_tail(pc2, f2 + 1)}}
    out = {"rows_total": len(rows), "rows_completed_valid": len(ok),
           "not_completed": [x for x in rows if x["status"] != "completed_valid"],
           "rho_R13": block(lambda x: x["panel"] == "rho"),
           "rho_j0": block(lambda x: x["panel"] == "j0"),
           "rho_all": block(lambda x: True),
           "per_rung_observed": {str(b): {"n": sum(1 for x in ok if x["bits"] == b),
                                          "fire_q1": sum(1 for x in ok if x["bits"] == b and x["q1"] < 0.9),
                                          "fire_q2": sum(1 for x in ok if x["bits"] == b and x["q2"] < 0.9)}
                                 for b in sorted({x["bits"] for x in ok})},
           "design_simulation": sim, "rows": rows}
    dump("05_ptm2_rho.json", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "design_simulation")}, indent=1))


if __name__ == "__main__":
    main()

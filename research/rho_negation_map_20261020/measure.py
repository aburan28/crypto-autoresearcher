#!/usr/bin/env python3
"""Paired measurement: index_calculus.rho on {X, -X} (negation) against the
walk on points (plain), on the same curve, target and seed.

For each size, CURVES prime-order curves (generate_prime_order_curve(bits, c))
and TARGETS planted logs per curve; each instance is solved by both walks with
the same seed.  The cost unit is walk_ops (walk group additions, look-ahead
and escapes included), divided by sqrt(N).  Output: results.json, one row per
solve, plus a per-size summary with a paired bootstrap of the ratio of means.
"""
import json
import math
import random
import statistics
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from crypto_autoresearcher.index_calculus import pollard_rho
from crypto_autoresearcher.index_calculus.curve import (
    generate_prime_order_curve,
)

BITS = [16, 20, 24, 28, 32]
CURVES, TARGETS = 8, 16
SEED = 20261020


def job(args):
    bits, c = args
    E, P = generate_prime_order_curve(bits, c)
    rng = random.Random(f"{SEED}|{bits}|{c}")
    rows = []
    for t in range(TARGETS):
        k = rng.randrange(1, E.order)
        Q = E.mul(k, P)
        for walk in ("negation", "plain"):
            t0 = time.perf_counter()
            rr = pollard_rho(E, P, Q, seed=SEED + 1000 * c + t, negation=walk == "negation")
            assert rr.verified and rr.k == k, (bits, c, t, walk)
            rows.append({"bits": bits, "curve": c, "target": t, "N": E.order, "walk": walk,
                         "walk_ops": rr.walk_ops, "setup_ops": rr.setup_ops,
                         "look_ahead_adds": rr.look_ahead_adds, "escapes": rr.escapes,
                         "canonicalisations": rr.canonicalisations, "walks": rr.walks,
                         "s_walk": rr.walk_ops / math.sqrt(E.order),
                         "seconds": time.perf_counter() - t0})
    return rows


def boot_ratio(pairs, reps=4000, seed=SEED):
    """Ratio of means plain/negation, resampling curves (clusters) then targets."""
    rng = random.Random(seed)
    by_curve = {}
    for c, neg, pl in pairs:
        by_curve.setdefault(c, []).append((neg, pl))
    keys = sorted(by_curve)
    out = []
    for _ in range(reps):
        sn = sp = 0.0
        for c in (rng.choice(keys) for _ in keys):
            for neg, pl in by_curve[c]:
                sn += neg; sp += pl
        out.append(sp / sn)
    out.sort()
    return out[int(0.025 * reps)], out[int(0.975 * reps) - 1]


def main():
    with Pool() as pool:
        rows = [r for rs in pool.map(job, [(b, c) for b in BITS for c in range(CURVES)]) for r in rs]
    summary = []
    for b in BITS + ["all"]:
        sel = [r for r in rows if b == "all" or r["bits"] == b]
        neg = [r for r in sel if r["walk"] == "negation"]
        pl = {(r["bits"], r["curve"], r["target"]): r for r in sel if r["walk"] == "plain"}
        pairs = [((r["bits"], r["curve"]), r["s_walk"], pl[(r["bits"], r["curve"], r["target"])]["s_walk"]) for r in neg]
        lo, hi = boot_ratio(pairs)
        mn, mp = statistics.mean(p[1] for p in pairs), statistics.mean(p[2] for p in pairs)
        steps = sum(r["walk_ops"] for r in neg)
        summary.append({"bits": b, "pairs": len(pairs),
                        "mean_s_walk_negation": mn, "mean_s_walk_plain": mp,
                        "negation_over_floor": mn / math.sqrt(math.pi / 4),
                        "plain_over_floor": mp / math.sqrt(math.pi / 2),
                        "ratio_plain_over_negation": mp / mn, "ratio_ci95": [lo, hi],
                        "look_ahead_share": sum(r["look_ahead_adds"] for r in neg) / steps,
                        "escape_share": sum(r["escapes"] for r in neg) / steps,
                        "wall_ratio_plain_over_negation":
                            sum(pl[(r["bits"], r["curve"], r["target"])]["seconds"] for r in neg)
                            / sum(r["seconds"] for r in neg)})
    Path("results.json").write_text(json.dumps({
        "schema": "rho-negation-map/v1", "seed": SEED, "bits": BITS, "curves": CURVES,
        "targets": TARGETS, "theory": {"negation": math.sqrt(math.pi / 4), "plain": math.sqrt(math.pi / 2),
                                       "ratio": math.sqrt(2)},
        "summary": summary, "rows": rows}, indent=1))
    for s in summary:
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}))


if __name__ == "__main__":
    main()

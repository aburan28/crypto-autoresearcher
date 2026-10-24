"""Exact probability, under the producer's sampler, of the relation family seen at p = 101
(validator TASK-20261022-67902e, phase 2 borderline probe).

For r = 2 and the short-model fit through integer lifts (x1, y1), (x2, y2), a direct computation
gives  2 P~1 + P~2 = O  <=>  (x1 - x2)^2 (2 x1 + x2) = (y1 - y2)^2,
and    2 P~1 - P~2 = O  <=>  (x1 - x2)^2 (2 x1 + x2) = (y1 + y2)^2   (and the same with 1 <-> 2).
Enumerates every lifted pair satisfying one of these, maps it to its unique curve (a, b) mod p,
and weights it by the sampler's probability: uniform nonsingular (a, b), P1 uniform over the
y != 0 affine points (n of them), P2 uniform over the n - 2 with a different x.
Each enumerated pair is re-verified with the sealed blind relation search. This is the
probability of THIS family only (a lower bound on the r = 2 dependence probability).
Usage: python3 -B -I accidental_rate.py OUT.json
"""
import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "blind"))
import relsearch as rs  # noqa: E402


def isqrt_exact(s):
    if s < 0:
        return None
    t = math.isqrt(s)
    return t if t * t == s else None


def count_points_y_nonzero(a, b, p, sqcount):
    return sum(sqcount[(x ** 3 + a * x + b) % p] for x in range(p))


def family_probability(p, verify=True):
    h = p // 2
    rng = range(-h, h + 1)
    sqcount = [0] * p
    for y in range(1, p):
        sqcount[y * y % p] += 1
    ncurves = sum(1 for a in range(p) for b in range(p) if (4 * a ** 3 + 27 * b * b) % p)
    tuples = set()
    for x1 in rng:
        for x2 in rng:
            if x1 == x2:
                continue
            for (u, v) in ((x1, x2), (x2, x1)):  # u is the doubled point
                t = isqrt_exact(2 * u + v)
                if t is None:
                    continue
                for yu in rng:
                    if yu == 0:
                        continue
                    for sgn in (1, -1):
                        for yv in (yu - sgn * t * (u - v), -(yu - sgn * t * (u - v))):
                            if yv == 0 or not (-h <= yv <= h):
                                continue
                            P = (x1, yu if u == x1 else yv)
                            Q = (x2, yv if u == x1 else yu)
                            tuples.add((P, Q))
    total, ncurve_cache, verified, checked, examples = 0.0, {}, 0, 0, []
    for (P, Q) in tuples:
        (x1, y1), (x2, y2) = P, Q
        a = ((y1 * y1 - x1 ** 3) - (y2 * y2 - x2 ** 3)) * pow(x1 - x2, -1, p) % p
        b = (y1 * y1 - x1 ** 3 - a * x1) % p
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        if (a, b) not in ncurve_cache:
            ncurve_cache[(a, b)] = count_points_y_nonzero(a, b, p, sqcount)
        n = ncurve_cache[(a, b)]
        total += 1.0 / (ncurves * n * (n - 2))
        if verify and (checked < 300):
            checked += 1
            E = rs.fit([P, Q])
            rels = rs.relation_search(E, [(Fr(x1), Fr(y1)), (Fr(x2), Fr(y2))], 6)
            ok = any(m in rels for m in ((2, 1), (2, -1), (1, 2), (1, -2)))
            verified += ok
            if len(examples) < 3:
                examples.append({"P": P, "Q": Q, "a": a, "b": b, "relations": rels})
    return {"p": p, "pairs_in_family": len(tuples), "verified_sample_size": checked, "per_trial_probability": total,
            "expected_in_100_r2_trials": 100 * total, "verified_by_blind_search": verified,
            "examples": examples}


if __name__ == "__main__":
    out = [family_probability(p) for p in (101, 211)]
    for o in out:
        o["P_at_least_one_in_100"] = 1 - (1 - o["per_trial_probability"]) ** 100
        o["P_at_least_one_in_200_(two_seeds)"] = 1 - (1 - o["per_trial_probability"]) ** 200
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1, default=str) + "\n")
    for o in out:
        print({k: v for k, v in o.items() if k != "examples"})

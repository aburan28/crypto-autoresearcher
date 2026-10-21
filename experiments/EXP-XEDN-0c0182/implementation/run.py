#!/usr/bin/env python3
"""EXP-XEDN-0c0182 driver: faithful-target eligibility census (H-XEDN-5befd8).

Standard library only. For the frozen source curve E^: y^2 = x(x^2 - x + 16)
over F_p, p in {31, 43, 59, 83} (the frozen manifest) and p = 353 (the
historical Cheon example), it records:

  F1  every odd-order affine point has x a nonzero quadratic residue;
  F2  sign eligibility of odd-order points (signed square s*t^2 == x, s = +-1)
      and the eligible arms of every faithful pair (both points of odd order)
      among the 32 frozen pairs, recomputed from the frozen t-rule;
  F4  Legendre symbols of D^ = A^2 - 4B = -63, of -1 and of -16;
  H1  exact accepted-cell counts per eligible (pair, arm) of the frozen
      proposal grid (A integral), beside the uniform-residue prediction.

The seed only drives the NON-frozen supplementary faithful-manifest proposal
(8 ordered odd-order pairs per prime); every other field is deterministic.
Writes raw-result.json and manifest.yaml into --run-dir. Exit 0 on a written
result, 3 on an internal consistency failure (implementation error).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

SCHEMA = "xedni.faithful_eligibility.result.v1"
A0, B0 = -1, 16
FROZEN_PRIMES = (31, 43, 59, 83)
HISTORICAL_P = 353
HISTORICAL_POINTS = ((9, 63), (17, 183))
T_MAX, T_REPS, SHIFT = 64, 4, 8
SIGNS = ((1, 1), (1, -1), (-1, 1), (-1, -1))


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def points(p: int) -> list[tuple[int, int]]:
    roots: dict[int, list[int]] = {}
    for y in range(p):
        roots.setdefault(y * y % p, []).append(y)
    out = []
    for x in range(p):
        rhs = x * (x * x + A0 * x + B0) % p
        for y in roots.get(rhs, []):
            out.append((x, y))
    return out


def add(P, Q, p):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + 2 * A0 * x1 + B0) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - A0 - x1 - x2) % p
    return (x3, (-(y1 + lam * (x3 - x1))) % p)


def mul(k, P, p):
    R, Q = None, P
    while k:
        if k & 1:
            R = add(R, Q, p)
        Q = add(Q, Q, p)
        k >>= 1
    return R


def odd_part(n: int) -> int:
    while n % 2 == 0:
        n //= 2
    return n


def t_reps(sign: int, x: int, p: int) -> list[int]:
    return [t for t in range(1, T_MAX + 1) if (sign * t * t - x) % p == 0][:T_REPS]


def uniform_prob(n: int, sp: int, sq: int, cache: dict) -> Fraction:
    """P[sp*w^2 == sq*z^2 mod |n|] for (w, z) uniform mod |n|."""
    m = abs(n)
    key = (m, sp * sq)
    if key not in cache:
        sq_count: dict[int, int] = {}
        for w in range(m):
            v = w * w % m
            sq_count[v] = sq_count.get(v, 0) + 1
        eps = sp * sq
        total = sum(c * sq_count.get((eps * v) % m, 0) for v, c in sq_count.items())
        cache[key] = Fraction(total, m * m)
    return cache[key]


def census(p: int) -> dict:
    pts = points(p)
    n_total = len(pts) + 1
    odd = odd_part(n_total)
    odd_pts = [P for P in pts if mul(odd, P, p) is None]
    f1_viol = [P for P in odd_pts if legendre(P[0], p) != 1]
    minus_ok = [P for P in odd_pts if legendre(-P[0], p) == 1]
    even_nonres = [P for P in pts if P not in odd_pts and legendre(P[0], p) == -1]
    return {
        "p": p, "p_mod_4": p % 4, "group_order": n_total, "odd_part": odd,
        "two_part": n_total // odd, "affine_points": len(pts),
        "odd_order_affine_points": len(odd_pts),
        "f1_violations": len(f1_viol), "f1_violation_points": [list(P) for P in f1_viol],
        "odd_order_points_with_minus_sign_eligible": len(minus_ok),
        "odd_order_points_with_plus_sign_eligible": sum(
            1 for P in odd_pts if legendre(P[0], p) == 1),
        "even_order_points_with_nonresidue_x": len(even_nonres),
        "legendre": {"D_minus_63": legendre(-63, p), "minus_1": legendre(-1, p),
                     "minus_16": legendre(-16, p)},
    }, set(odd_pts)


def accepted_cells(pair: dict, sp: int, sq: int, reps_p, reps_q, cache) -> dict:
    p = pair["p"]
    (xp, yp), (xq, yq) = pair["P"], pair["Q"]
    accepted = reduced_ok = bad_disc = 0
    predicted = Fraction(0)
    cells = 0
    for s in reps_p:
        w0 = yp * pow(s, -1, p) % p
        for t in reps_q:
            z0 = yq * pow(t, -1, p) % p
            n = sp * s * s - sq * t * t
            if n == 0:
                raise SystemExit(3)
            predicted += 289 * uniform_prob(n, sp, sq, cache)
            for j in range(-SHIFT, SHIFT + 1):
                w = w0 + p * j
                for k in range(-SHIFT, SHIFT + 1):
                    z = z0 + p * k
                    cells += 1
                    num = sp * w * w - sq * z * z - s ** 4 + t ** 4
                    if num % n:
                        continue
                    A = num // n
                    B = sp * w * w - s ** 4 - sp * A * s * s
                    if B * (A * A - 4 * B) == 0:
                        bad_disc += 1
                        continue
                    accepted += 1
                    if (A - A0) % p == 0 and (B - B0) % p == 0:
                        reduced_ok += 1
    return {"cells": cells, "accepted": accepted, "accepted_reducing_to_source": reduced_ok,
            "rejected_zero_discriminant": bad_disc,
            "h1_predicted": float(predicted), "h1_predicted_exact": str(predicted)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--trial-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--targets", required=True)
    args = ap.parse_args()
    start = time.time()
    targets_bytes = Path(args.targets).read_bytes()
    targets = json.loads(targets_bytes)
    primes = list(FROZEN_PRIMES) + [HISTORICAL_P]
    per_prime, odd_sets = [], {}
    for p in primes:
        row, odd_set = census(p)
        per_prime.append(row)
        odd_sets[p] = odd_set
    cache: dict = {}
    pairs_out = []
    rep_mismatch = 0
    for pair in targets["pairs"]:
        p = pair["p"]
        P, Q = tuple(pair["P"]), tuple(pair["Q"])
        p_odd, q_odd = P in odd_sets[p], Q in odd_sets[p]
        arms = []
        for arm in pair["arms"]:
            sp, sq = arm["signs"]
            rp, rq = t_reps(sp, P[0], p), t_reps(sq, Q[0], p)
            if [rp, rq] != arm["t_representatives"]:
                rep_mismatch += 1
            eligible = bool(rp and rq)
            row = {"signs": [sp, sq], "eligible": eligible,
                   "frozen_proposal_cells": arm["proposal_cells"]}
            if eligible:
                row.update(accepted_cells(pair, sp, sq, rp, rq, cache))
            arms.append(row)
        pairs_out.append({"id": pair["id"], "p": p, "P_odd_order": p_odd,
                          "Q_odd_order": q_odd, "faithful": p_odd and q_odd, "arms": arms})
    if rep_mismatch:
        print(f"t-representative recomputation disagrees with frozen targets on {rep_mismatch} arms",
              file=sys.stderr)
        return 3
    faithful = [r for r in pairs_out if r["faithful"]]
    nonplus_faithful_3mod4 = sum(
        1 for r in faithful if r["p"] % 4 == 3
        for a in r["arms"] if a["eligible"] and a["signs"] != [1, 1])
    by_arm: dict[str, dict] = {}
    for r in pairs_out:
        for a in r["arms"]:
            if not a["eligible"]:
                continue
            key = f"p{r['p']}:{a['signs'][0]:+d}{a['signs'][1]:+d}"
            agg = by_arm.setdefault(key, {"accepted": 0, "h1_predicted": 0.0, "eligible_pairs": 0})
            agg["accepted"] += a["accepted"]
            agg["h1_predicted"] += a["h1_predicted"]
            agg["eligible_pairs"] += 1
    rng = random.Random(args.seed)
    manifest_proposal = {}
    for p in FROZEN_PRIMES:
        odd = sorted(odd_sets[p])
        cand = [(P, Q) for P in odd for Q in odd if P[0] != Q[0]]
        pick = rng.sample(cand, min(8, len(cand))) if cand else []
        manifest_proposal[str(p)] = [[list(P), list(Q)] for P, Q in pick]
    hist = {"p": HISTORICAL_P, "points": [list(P) for P in HISTORICAL_POINTS],
            "on_curve": [all((y * y - x * (x * x + A0 * x + B0)) % HISTORICAL_P == 0
                             for x, y in HISTORICAL_POINTS)],
            "x_residue": [legendre(x, HISTORICAL_P) for x, _ in HISTORICAL_POINTS],
            "minus_x_residue": [legendre(-x, HISTORICAL_P) for x, _ in HISTORICAL_POINTS],
            "odd_order": [tuple(P) in odd_sets[HISTORICAL_P] for P in HISTORICAL_POINTS]}
    result = {
        "schema": SCHEMA, "experiment_id": "EXP-XEDN-0c0182", "hypothesis_id": "H-XEDN-5befd8",
        "run_id": args.run_id, "trial_id": args.trial_id, "seed": args.seed,
        "source_curve": {"A": A0, "B": B0}, "primes": primes,
        "targets_sha256": hashlib.sha256(targets_bytes).hexdigest(),
        "frozen_pairs": len(pairs_out),
        "per_prime": per_prime,
        "f1_violations_total": sum(r["f1_violations"] for r in per_prime),
        "odd_order_minus_eligible_at_3mod4": sum(
            r["odd_order_points_with_minus_sign_eligible"] for r in per_prime if r["p_mod_4"] == 3),
        "faithful_pairs": len(faithful),
        "faithful_pair_ids": [r["id"] for r in faithful],
        "faithful_nonplus_eligible_arms_at_3mod4": nonplus_faithful_3mod4,
        "pairs": pairs_out, "accepted_by_arm": by_arm,
        "historical_control": hist,
        "supplementary_manifest_proposal": {"frozen": False, "seed": args.seed,
                                            "pairs_by_prime": manifest_proposal},
        "elapsed_seconds": round(time.time() - start, 3),
    }
    out = Path(args.run_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "raw-result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    (out / "manifest.yaml").write_text(
        f"run_id: {args.run_id}\ntrial_id: {args.trial_id}\nseed: {args.seed}\nstatus: output_written\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

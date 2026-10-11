#!/usr/bin/env python3
"""EXP-ECDLP-2535ec: paired-prime positive control (multiplicative side).

Counts doubly smooth (a, b) pairs for three NFS polynomial arms on the shared
toy prime set and reports the special-over-null yield ratios with bootstrap
intervals. Pure Python 3 standard library. Writes raw-result.json and
manifest.yaml into --out. It records observations only; it interprets nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import primeset  # noqa: E402


def poly_eval(coeffs: list[int], x: int) -> int:
    v = 0
    for c in reversed(coeffs):
        v = v * x + c
    return v


def homog_norm(coeffs: list[int], a: int, b: int) -> int:
    """F(a, b) = sum f_i a^i b^(d-i) for coeffs low-to-high of degree d."""
    d = len(coeffs) - 1
    total = 0
    for i, f in enumerate(coeffs):
        total += f * a ** i * b ** (d - i)
    return total


def is_smooth(n: int, primes: list[int], bound: int) -> bool:
    n = abs(n)
    if n == 0:
        return False
    for q in primes:
        if q > bound:
            break
        while n % q == 0:
            n //= q
        if n == 1:
            return True
        if q * q > n:
            return n <= bound
    return n == 1


def build_arms(d: int, bits: int, seed: int) -> dict:
    sp = primeset.special_primes(d, bits, 1)
    if not sp:
        raise SystemExit(f"no special prime for d={d} bits={bits}")
    sp = sp[0]
    p, m, c = sp["p"], sp["m"], sp["c"]
    rng = random.Random(f"EXP-ECDLP-2535ec:{seed}:{d}:{bits}")
    lo, hi = max(1, m // (8 * d)), max(1, m // (4 * d))
    t = rng.randint(lo, hi)
    m0 = m - t
    f0 = primeset.monic_base_m_poly(p, m0, d)
    rp = primeset.matched_random_prime(bits, seed, f"d{d}")
    pp = rp["p"]
    mp = int(round(pp ** (1.0 / d)))
    while mp ** d > pp:
        mp -= 1
    fp = primeset.monic_base_m_poly(pp, mp, d)
    arms = {
        "special": {"p": p, "m": m, "f": [-c] + [0] * (d - 1) + [1]},
        "null_same_prime": {"p": p, "m": m0, "f": f0, "t": t},
        "null_random_prime": {"p": pp, "m": mp, "f": fp, "start": rp["start"]},
    }
    for name, arm in arms.items():
        if arm["f"] is None:
            raise SystemExit(f"{name}: base-m expansion does not fit (d={d}, bits={bits})")
        if poly_eval(arm["f"], arm["m"]) != arm["p"]:
            raise SystemExit(f"{name}: CTRL-ROOT failed")
        arm["ctrl_root"] = True
    return {"d": d, "bits": bits, "seed": seed, "c": c, "arms": arms}


def bootstrap_ratio(cat_counts: dict, rng: random.Random, reps: int) -> dict:
    """cat_counts: {'both': n11, 'special_only': n10, 'null_only': n01, 'neither': n00}."""
    n = sum(cat_counts.values())
    keys = ["both", "special_only", "null_only", "neither"]
    probs = [cat_counts[k] / n for k in keys]
    ratios = []
    for _ in range(reps):
        draws = multinomial(n, probs, rng)
        s = draws[0] + draws[1]
        u = draws[0] + draws[2]
        ratios.append(s / u if u else float("inf"))
    finite = sorted(r for r in ratios if math.isfinite(r))
    if len(finite) < reps // 2:
        return {"ci95": None, "infinite_fraction": 1 - len(finite) / reps}
    lo = finite[int(0.025 * len(finite))]
    hi = finite[min(len(finite) - 1, int(0.975 * len(finite)))]
    return {"ci95": [lo, hi], "infinite_fraction": 1 - len(finite) / reps}


def multinomial(n: int, probs: list[float], rng: random.Random) -> list[int]:
    out = []
    remaining = n
    rest = 1.0
    for pr in probs[:-1]:
        q = 0.0 if rest <= 0 else min(1.0, pr / rest)
        k = binomial(remaining, q, rng)
        out.append(k)
        remaining -= k
        rest -= pr
    out.append(remaining)
    return out


def binomial(n: int, q: float, rng: random.Random) -> int:
    if n == 0 or q <= 0:
        return 0
    if q >= 1:
        return n
    if hasattr(rng, "binomialvariate"):
        return rng.binomialvariate(n, q)
    return sum(1 for _ in range(n) if rng.random() < q)


def score_cell(cell: dict, A: int, Bs: int, primes: list[int], rng: random.Random) -> dict:
    arms = cell["arms"]
    names = list(arms)
    counts = {k: 0 for k in names}
    zero = {k: 0 for k in names}
    log2alg = {k: [] for k in names}
    log2rat = {k: [] for k in names}
    min_norm = {k: None for k in names}
    cat = {"special_vs_null_same_prime": {"both": 0, "special_only": 0, "null_only": 0, "neither": 0},
           "special_vs_null_random_prime": {"both": 0, "special_only": 0, "null_only": 0, "neither": 0}}
    pairs = 0
    t0 = time.time()
    for b in range(1, A + 1):
        for a in range(-A, A + 1):
            if math.gcd(a, b) != 1:
                continue
            pairs += 1
            smooth = {}
            for k in names:
                arm = arms[k]
                rat = a + b * arm["m"]
                alg = homog_norm(arm["f"], a, b)
                if alg == 0 or rat == 0:
                    zero[k] += 1
                    smooth[k] = False
                    continue
                la = math.log2(abs(alg))
                log2alg[k].append(la)
                log2rat[k].append(math.log2(abs(rat)))
                if min_norm[k] is None or abs(alg) < min_norm[k]:
                    min_norm[k] = abs(alg)
                smooth[k] = is_smooth(rat, primes, Bs) and is_smooth(alg, primes, Bs)
                if smooth[k]:
                    counts[k] += 1
            for key, other in (("special_vs_null_same_prime", "null_same_prime"),
                               ("special_vs_null_random_prime", "null_random_prime")):
                s, u = smooth["special"], smooth[other]
                cat[key]["both" if s and u else "special_only" if s else "null_only" if u else "neither"] += 1
    out = {
        "A": A, "B_s": Bs, "coprime_pairs": pairs,
        "counted_doubly_smooth_pairs": counts,
        "zero_norm_count": zero,
        "mean_log2_algebraic_norm": {k: statistics.fmean(v) if v else None for k, v in log2alg.items()},
        "median_log2_algebraic_norm": {k: statistics.median(v) if v else None for k, v in log2alg.items()},
        "mean_log2_rational_side": {k: statistics.fmean(v) if v else None for k, v in log2rat.items()},
        "min_algebraic_norm": min_norm,
        "wall_clock_seconds": time.time() - t0,
    }
    ratios = {}
    for key, other in (("special_vs_null_same_prime", "null_same_prime"),
                       ("special_vs_null_random_prime", "null_random_prime")):
        u = counts[other]
        ratios[key] = {"ratio": counts["special"] / u if u else None,
                       "bootstrap": bootstrap_ratio(cat[key], rng, 1000),
                       "categories": cat[key]}
    out["yield_ratio"] = ratios
    out["ctrl_same_box"] = True
    d = cell["d"]
    m = arms["special"]["m"]
    direction_ok = {}
    for other in ("null_same_prime", "null_random_prime"):
        ms, mo = out["mean_log2_algebraic_norm"]["special"], out["mean_log2_algebraic_norm"][other]
        coeff_gap = math.log2(max(abs(f) for f in arms[other]["f"][:-1]) / max(1, abs(cell["c"])))
        direction_ok[other] = {"pass": ms is not None and mo is not None and mo > ms,
                               "measured_gap_bits": None if ms is None or mo is None else mo - ms,
                               "coefficient_gap_bits": coeff_gap}
    out["ctrl_predicted_direction"] = direction_ok
    a1, a2 = out["mean_log2_algebraic_norm"]["null_same_prime"], out["mean_log2_algebraic_norm"]["null_random_prime"]
    c1, c2 = counts["null_same_prime"], counts["null_random_prime"]
    out["ctrl_null_null"] = {
        "log2_mean_gap": None if a1 is None or a2 is None else abs(a1 - a2),
        "yield_factor": None if min(c1, c2) == 0 else max(c1, c2) / min(c1, c2),
        "pass": (a1 is not None and a2 is not None and abs(a1 - a2) <= 2.0
                 and min(c1, c2) > 0 and max(c1, c2) / min(c1, c2) <= 2.0),
    }
    return out


def git_info() -> dict:
    try:
        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
        return {"root": root, "commit": commit, "dirty": dirty}
    except Exception as error:  # noqa: BLE001
        return {"error": str(error)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", type=int, nargs="+", default=[3, 4, 5])
    ap.add_argument("--bits", type=int, nargs="+", default=[30, 40])
    ap.add_argument("--A", type=int, nargs="+", default=[150, 300])
    ap.add_argument("--Bs", type=int, nargs="+", default=[512, 2048])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    primes = primeset.primes_upto(max(args.Bs))
    started = time.time()
    cells = []
    for d in args.d:
        for bits in args.bits:
            for seed in args.seeds:
                cell = build_arms(d, bits, seed)
                rng = random.Random(f"EXP-ECDLP-2535ec:bootstrap:{seed}:{d}:{bits}")
                cell["results"] = [score_cell(cell, A, Bs, primes, rng)
                                   for A in args.A for Bs in args.Bs]
                cells.append(cell)
                print(f"cell d={d} bits={bits} seed={seed} p={cell['arms']['special']['p']} done",
                      file=sys.stderr, flush=True)
    raw = {"experiment_id": "EXP-ECDLP-2535ec", "hypothesis_id": "H-ECDLP-bd1572",
           "argv": sys.argv, "cells": cells, "wall_clock_seconds": time.time() - started}
    raw_path = os.path.join(args.out, "raw-result.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True)
    src = os.path.abspath(__file__)
    manifest = {
        "experiment_id": "EXP-ECDLP-2535ec",
        "command": " ".join(sys.argv),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git": git_info(),
        "source_sha256": {os.path.basename(src): hashlib.sha256(open(src, "rb").read()).hexdigest(),
                          "primeset.py": hashlib.sha256(open(os.path.join(os.path.dirname(src), "primeset.py"), "rb").read()).hexdigest()},
        "raw_result_sha256": hashlib.sha256(open(raw_path, "rb").read()).hexdigest(),
        "started_unix": started, "finished_unix": time.time(),
        "status": "completed_valid" if all(r["ctrl_same_box"] for c in cells for r in c["results"]) else "completed_invalid",
        "asserts_nothing_about": "the hypothesis; observations only",
    }
    with open(os.path.join(args.out, "manifest.yaml"), "w", encoding="utf-8") as fh:
        for k, v in manifest.items():
            fh.write(f"{k}: {json.dumps(v)}\n")


if __name__ == "__main__":
    main()

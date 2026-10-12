#!/usr/bin/env python3
"""EXP-ECDLP-ad27ad (H-ECDLP-986bab, SNFS-G4): rotation-class factor base control.

For Mersenne primes p = 2^c - 1 multiplication by 2 is a cyclic bit rotation.
D_rot(m) = {P : rotmin(x(P)) < 2^(c-m)}. Measures the closure ratio
Pr[P+Q in D | P,Q in D] / Pr[P in D] and the decomposition ratio
Pr[R-P in D | P in D] / Pr[P in D] against (i) a keyed-hash subset of the
same density on the same curve and (ii) a size-based subset of the same
density over a matched random prime; exact cross-checks at c <= 17.
Pure Python 3 standard library. Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import primeset  # noqa: E402

EXP = "EXP-ECDLP-ad27ad"
HYP = "H-ECDLP-986bab"


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_sub(P, Q, p, a):
    return ec_add(P, None if Q is None else (Q[0], (-Q[1]) % p), a, p)


def sqrt_mod(n, p):
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        bexp = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, bexp * bexp % p, t * bexp * bexp % p, r * bexp % p
    return r


def random_point(p, a, b, rng):
    while True:
        x = rng.randrange(p)
        v = (x * x * x + a * x + b) % p
        if v == 0:
            continue
        if pow(v, (p - 1) // 2, p) == 1:
            y = sqrt_mod(v, p)
            return (x, y if rng.random() < 0.5 else p - y)


def rotmin(x, c):
    """Least integer among the c cyclic rotations of the c-bit string of x (x = p reads as 0)."""
    mask = (1 << c) - 1
    x &= mask
    best = x
    r = x
    for _ in range(c - 1):
        r = ((r << 1) | (r >> (c - 1))) & mask
        if r < best:
            best = r
    return best


def make_membership(kind, c, m, p, key):
    thr_rot = 1 << (c - m)
    if kind == "rot":
        return lambda x: rotmin(x, c) < thr_rot
    if kind == "hash":
        thr_h = 1 << (64 - m)
        def mem(x):
            h = hashlib.blake2b(f"{key}:{x}".encode(), digest_size=8).digest()
            return int.from_bytes(h, "big") < thr_h
        return mem
    if kind == "size":
        thr_s = p >> m
        return lambda x: x < thr_s
    raise ValueError(kind)


def cell(p, a, b, c, m, kind, key, pairs, targets, per_target, rng):
    mem = make_membership(kind, c, m, p, key)
    # density on points
    hits = 0
    dens_n = 20000
    for _ in range(dens_n):
        hits += mem(random_point(p, a, b, rng)[0])
    dens = hits / dens_n
    # closure
    def sample_in_D():
        while True:
            P = random_point(p, a, b, rng)
            if mem(P[0]):
                return P
    clos = 0
    for _ in range(pairs):
        P, Q = sample_in_D(), sample_in_D()
        S = ec_add(P, Q, a, p)
        if S is not None and mem(S[0]):
            clos += 1
    cf = clos / pairs
    # decomposition
    dec = 0
    tot = 0
    for _ in range(targets):
        R = random_point(p, a, b, rng)
        for _ in range(per_target):
            P = sample_in_D()
            T = ec_sub(R, P, p, a)
            tot += 1
            if T is not None and mem(T[0]):
                dec += 1
    df = dec / tot
    se_c = math.sqrt(cf * (1 - cf) / pairs) if 0 < cf < 1 else 0.0
    se_d = math.sqrt(df * (1 - df) / tot) if 0 < df < 1 else 0.0
    return {"kind": kind, "m": m, "density": dens, "closure_fraction": cf, "closure_ratio": cf / dens,
            "closure_ratio_se": se_c / dens, "decomposition_fraction": df, "decomposition_ratio": df / dens,
            "decomposition_ratio_se": se_d / dens, "pairs": pairs, "targets": targets, "per_target": per_target}


def exhaustive_check(p, a, b, c, m, rng, targets=20):
    """c <= 17: enumerate E(F_p), exact density of D_rot and exact decomposition count for a few targets."""
    pts = []
    table = bytearray(p)
    for y in range(p):
        table[y * y % p] = 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v == 0:
            pts.append((x, 0))
        elif table[v]:
            y = sqrt_mod(v, p)
            pts.append((x, y))
            pts.append((x, p - y))
    thr = 1 << (c - m)
    D = [P for P in pts if rotmin(P[0], c) < thr]
    dens = len(D) / len(pts)
    counts = []
    for _ in range(targets):
        R = pts[rng.randrange(len(pts))]
        n = 0
        for P in D:
            T = ec_sub(R, P, p, a)
            if T is not None and rotmin(T[0], c) < thr:
                n += 1
        counts.append(n / len(D))
    mean = sum(counts) / len(counts)
    return {"n_points": len(pts), "n_D": len(D), "exact_density": dens,
            "exact_decomposition_fraction_mean": mean, "exact_decomposition_ratio": mean / dens}


def membership_cost(c, n, rng):
    xs = [rng.randrange(1 << c) for _ in range(n)]
    t0 = time.perf_counter()
    for x in xs:
        rotmin(x, c)
    return (time.perf_counter() - t0) / n * 1e6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c", type=int, nargs="+", default=[13, 17, 19, 31, 61])
    ap.add_argument("--m", type=int, nargs="+", default=[1, 2, 4])
    ap.add_argument("--curves", type=int, default=2)
    ap.add_argument("--pairs", type=int, default=40000)
    ap.add_argument("--targets", type=int, default=100)
    ap.add_argument("--per-target", type=int, default=400)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--exhaustive-max-c", type=int, default=17)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()
    raw = {"experiment_id": EXP, "hypothesis_id": HYP, "argv": sys.argv, "cells": []}
    for seed in args.seeds:
        for c in args.c:
            p = 2 ** c - 1
            assert primeset.is_prime(p)
            rp = primeset.matched_random_prime(c, seed, f"rot-c{c}")["p"]
            rng = random.Random(f"{EXP}:{seed}:{c}")
            for ci in range(args.curves):
                while True:
                    a, b = rng.randrange(p), rng.randrange(p)
                    if (4 * a * a * a + 27 * b * b) % p:
                        break
                while True:
                    ar, br = rng.randrange(rp), rng.randrange(rp)
                    if (4 * ar * ar * ar + 27 * br * br) % rp:
                        break
                for m in args.m:
                    rec = {"seed": seed, "c": c, "p": p, "curve": ci, "a": a, "b": b, "random_prime": rp, "m": m}
                    rec["rot"] = cell(p, a, b, c, m, "rot", None, args.pairs, args.targets, args.per_target, rng)
                    rec["hash"] = cell(p, a, b, c, m, "hash", f"{seed}:{c}:{ci}", args.pairs, args.targets, args.per_target, rng)
                    rec["size_random_prime"] = cell(rp, ar, br, c, m, "size", None, args.pairs, args.targets, args.per_target, rng)
                    if c <= args.exhaustive_max_c and ci == 0:
                        rec["exhaustive"] = exhaustive_check(p, a, b, c, m, rng)
                    raw["cells"].append(rec)
                    print(f"c={c} seed={seed} curve={ci} m={m} rot={rec['rot']['closure_ratio']:.3f} "
                          f"hash={rec['hash']['closure_ratio']:.3f} size={rec['size_random_prime']['closure_ratio']:.3f}",
                          file=sys.stderr, flush=True)
    raw["membership_cost_us"] = {str(c): membership_cost(c, 20000, random.Random(f"{EXP}:cost:{c}")) for c in args.c}
    # summary: max |ratio - 1| per kind, and rot-minus-hash differences in SE units
    summ = {}
    for kind in ("rot", "hash", "size_random_prime"):
        summ[kind] = {"max_abs_closure_dev": max(abs(x[kind]["closure_ratio"] - 1) for x in raw["cells"]),
                      "max_abs_decomposition_dev": max(abs(x[kind]["decomposition_ratio"] - 1) for x in raw["cells"]),
                      "cells_outside_closure_band": sum(1 for x in raw["cells"] if abs(x[kind]["closure_ratio"] - 1) > max(0.03, 3 * x[kind]["closure_ratio_se"])),
                      "cells_outside_decomposition_band": sum(1 for x in raw["cells"] if abs(x[kind]["decomposition_ratio"] - 1) > max(0.05, 3 * x[kind]["decomposition_ratio_se"]))}
    diffs = []
    for x in raw["cells"]:
        se = math.hypot(x["rot"]["closure_ratio_se"], x["hash"]["closure_ratio_se"]) or 1e-9
        diffs.append((x["rot"]["closure_ratio"] - x["hash"]["closure_ratio"]) / se)
    summ["rot_minus_hash_closure_z"] = {"max_abs": max(abs(d) for d in diffs),
                                        "cells_beyond_3se": sum(1 for d in diffs if abs(d) > 3)}
    raw["summary"] = summ
    raw["wall_clock_seconds"] = time.time() - started
    raw_path = os.path.join(args.out, "raw-result.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True, default=str)
    src = os.path.abspath(__file__)
    here = os.path.dirname(src)
    manifest = {"experiment_id": EXP, "command": " ".join(sys.argv), "python": platform.python_version(),
                "platform": platform.platform(),
                "source_sha256": {"run.py": hashlib.sha256(open(src, "rb").read()).hexdigest(),
                                  "primeset.py": hashlib.sha256(open(os.path.join(here, "primeset.py"), "rb").read()).hexdigest()},
                "raw_result_sha256": hashlib.sha256(open(raw_path, "rb").read()).hexdigest(),
                "started_unix": started, "finished_unix": time.time(),
                "asserts_nothing_about": "the hypothesis; observations only"}
    try:
        manifest["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        manifest["git_commit"] = None
    with open(os.path.join(args.out, "manifest.yaml"), "w", encoding="utf-8") as fh:
        for k, v in manifest.items():
            fh.write(f"{k}: {json.dumps(v)}\n")


if __name__ == "__main__":
    main()

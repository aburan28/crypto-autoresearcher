#!/usr/bin/env python3
"""EXP-ECDLP-8cc60d (H-ECDLP-281dd6, SNFS-G2): embedding degree over Mersenne primes.

Part A: census of seeded random curves over toy Mersenne primes p = 2^c - 1
versus matched random primes; the four exact conditions (k = 1 iff ord_l(2) |
c - 1; k != 2; k = 3 iff ord_l(2^c) = 6; k = 4 iff l | 2^(2c-1) - 2^c + 1)
are checked on every Mersenne row; pre-registered arm tests.
Part B: census of curve orders whose large prime factor l has ord_l(2) <= 10^4,
against the index-heuristic prediction.
Part C: deployed public curves (P-521, P-192, P-224, P-256): ord_l(p) > cap by
direct exponentiation; for P-521 also the four exact conditions modulo l.
Part D: modeled algebraic-norm sizes at p = 2^521 - 1 for x^5 - 16 versus the
base-m expansion 2^101 x^4 - 1 at m = 2^105 over seeded boxes; no sieving.
Pure Python 3 standard library. Observations only; asserts nothing about the
hypothesis.
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

EXP = "EXP-ECDLP-8cc60d"
HYP = "H-ECDLP-281dd6"

# ----------------------------------------------------------------------------
# curve arithmetic (affine short Weierstrass), any p
# ----------------------------------------------------------------------------


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


def ec_neg(P, p):
    return None if P is None else (P[0], (-P[1]) % p)


def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R


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
            return (x, 0)
        if pow(v, (p - 1) // 2, p) == 1:
            return (x, sqrt_mod(v, p))


def count_points_exact(p, a, b):
    table = bytearray(p)
    for y in range(p):
        table[y * y % p] = 1
    total = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v == 0:
            continue
        total += 1 if table[v] else -1
    return total


def order_candidates_bsgs(P, a, p):
    """All N in the Hasse interval with [N]P = O (baby-step giant-step)."""
    w = math.isqrt(p)
    lo = p + 1 - 2 * w - 1
    width = 4 * w + 3
    m = math.isqrt(width) + 1
    baby = {}
    R = None
    for j in range(m):
        baby.setdefault(R, j)      # R = [j]P (None at j = 0)
        R = ec_add(R, P, a, p)
    mP = R                          # [m]P
    base = ec_mul(lo, P, a, p)      # [lo]P
    cands = set()
    for i in range(m + 2):
        # base = [lo + i m]P ; a match base == [j]P gives N = lo + i m - j ;
        # base == -[j]P gives N = lo + i m + j
        if base in baby:
            cands.add(lo + i * m - baby[base])
        if ec_neg(base, p) in baby:
            cands.add(lo + i * m + baby[ec_neg(base, p)])
        base = ec_add(base, mP, a, p)
    return {N for N in cands if lo <= N <= lo + width and ec_mul(N, P, a, p) is None}


def count_points_bsgs(p, a, b, rng, tries=6):
    cands = None
    for _ in range(tries):
        P = random_point(p, a, b, rng)
        c = order_candidates_bsgs(P, a, p)
        cands = c if cands is None else (cands & c)
        if len(cands) == 1:
            return next(iter(cands)), True
    return (next(iter(cands)) if cands else None), False


def factor_small(n):
    f = {}
    q = 2
    while q * q <= n:
        while n % q == 0:
            f[q] = f.get(q, 0) + 1
            n //= q
        q += 1 if q == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def mult_order_exact(g, l):
    """Exact multiplicative order of g modulo the prime l via the factorisation of l - 1."""
    g %= l
    if g == 0:
        return None
    order = l - 1
    for q in factor_small(l - 1):
        while order % q == 0 and pow(g, order // q, l) == 1:
            order //= q
    return order


def mult_order_capped(g, l, cap):
    x = g % l
    v = x
    k = 1
    while v != 1:
        v = v * x % l
        k += 1
        if k > cap:
            return None
    return k


def exact_conditions(k, l, c, o2):
    """The four exact statements for p = 2^c - 1 and odd l (each must be True)."""
    k1 = (k == 1) == ((c - 1) % o2 == 0)                       # Phi_1(p) = 2 (2^(c-1) - 1)
    k2 = (k != 2)                                              # Phi_2(p) = 2^c
    k3 = (k == 3) == (mult_order_exact(pow(2, c, l), l) == 6)  # Phi_3(p) = Phi_6(2^c)
    k4 = (k == 4) == ((pow(2, 2 * c - 1, l) - pow(2, c, l) + 1) % l == 0)  # Phi_4(p)/2 Aurifeuillean
    return {"k1_iff_ord2_divides_c_minus_1": k1, "k_never_2": k2,
            "k3_iff_ord_2c_is_6": k3, "k4_iff_l_divides_aurifeuillean": k4}


# ----------------------------------------------------------------------------
# part A: census
# ----------------------------------------------------------------------------


def census(p, arm, c, curves, seed, exact_limit):
    rng = random.Random(f"{EXP}:{seed}:{arm}:{p}")
    rows, anomalous, even_l, ambiguous = [], 0, 0, 0
    ctrl = None
    while len(rows) + anomalous + even_l + ambiguous < curves:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a * a * a + 27 * b * b) % p == 0:
            continue
        if p < exact_limit:
            n = count_points_exact(p, a, b)
            n2, ok = count_points_bsgs(p, a, b, random.Random(f"{EXP}:bsgs:{seed}:{a}:{b}"))
            if ctrl is None:
                ctrl = {"a": a, "b": b, "exact": n, "bsgs": n2, "agree": (n == n2) and ok}
            if not (ok and n == n2):
                ctrl = dict(ctrl or {}, failure={"a": a, "b": b, "exact": n, "bsgs": n2, "unique": ok})
        else:
            n, ok = count_points_bsgs(p, a, b, random.Random(f"{EXP}:bsgs:{seed}:{a}:{b}"))
            if not ok:
                ambiguous += 1
                continue
            if ctrl is None:
                P = random_point(p, a, b, rng)
                ctrl = {"a": a, "b": b, "bsgs": n, "hasse": abs(n - p - 1) <= 2 * math.isqrt(p) + 1,
                        "point_killed": ec_mul(n, P, a, p) is None}
        if n == p:
            anomalous += 1
            continue
        l = max(factor_small(n))
        if l == 2:
            even_l += 1
            continue
        k = mult_order_exact(p, l)
        row = {"a": a, "b": b, "order": n, "l": l, "k": k, "t": (l - 1) // k}
        if arm == "mersenne":
            o2 = mult_order_exact(2, l)
            row["ord_l_2"] = o2
            row["exact_conditions"] = exact_conditions(k, l, c, o2)
            row["identity_ok"] = all(row["exact_conditions"].values())
            row["small_ord_l_2"] = o2 <= 10 ** 4
        rows.append(row)
    out = {"p": p, "c": c if arm == "mersenne" else None, "arm": arm, "rows": rows,
           "anomalous": anomalous, "even_l": even_l, "ambiguous_order": ambiguous, "ctrl_count": ctrl}
    if p % 4 == 3:  # y^2 = x^3 + x is supersingular, #E = p + 1
        n = p + 1
        if p < exact_limit:
            assert count_points_exact(p, 1, 0) == n
        fac = factor_small(n)
        l = max(fac)
        out["supersingular_control"] = {"order": n, "factorisation": {str(q): e for q, e in fac.items()},
                                        "l": l, "k": (mult_order_exact(p, l) if l > 2 else None),
                                        "two_group": (set(fac) == {2})}
    return out


def ks_statistic(xs, ys):
    xs, ys = sorted(xs), sorted(ys)
    i = j = 0
    d = 0.0
    n, m = len(xs), len(ys)
    while i < n and j < m:
        if xs[i] <= ys[j]:
            i += 1
        else:
            j += 1
        d = max(d, abs(i / n - j / m))
    return d


def arm_tests(cells, seed, reps=5000):
    rng = random.Random(f"{EXP}:perm:{seed}")
    sp = [r for cell in cells for r in cell["census"]["rows"] if cell["census"]["arm"] == "mersenne"]
    rd = [r for cell in cells for r in cell["census"]["rows"] if cell["census"]["arm"] == "random"]
    xs = [math.log2(r["t"]) for r in sp]
    ys = [math.log2(r["t"]) for r in rd]
    obs = statistics.fmean(xs) - statistics.fmean(ys)
    obs_ks = ks_statistic(xs, ys)
    pooled = xs + ys
    n = len(xs)
    cnt_mean = cnt_ks = 0
    for _ in range(reps):
        rng.shuffle(pooled)
        if abs(statistics.fmean(pooled[:n]) - statistics.fmean(pooled[n:])) >= abs(obs):
            cnt_mean += 1
        if ks_statistic(pooled[:n], pooled[n:]) >= obs_ks:
            cnt_ks += 1
    f1 = sum(1 for r in sp if r["k"] <= 20) / len(sp)
    f2 = sum(1 for r in rd if r["k"] <= 20) / len(rd)
    se = math.sqrt(f1 * (1 - f1) / len(sp) + f2 * (1 - f2) / len(rd))
    return {"mean_log2_t": {"mersenne": statistics.fmean(xs), "random": statistics.fmean(ys),
                            "difference": obs, "permutation_p_value": (cnt_mean + 1) / (reps + 1)},
            "ks_log2_t": {"statistic": obs_ks, "permutation_p_value": (cnt_ks + 1) / (reps + 1)},
            "small_k_fraction": {"mersenne": f1, "random": f2, "difference": f1 - f2, "standard_error": se,
                                 "z": ((f1 - f2) / se if se > 0 else 0.0)},
            "k_equals_2_count": {"mersenne": sum(1 for r in sp if r["k"] == 2),
                                 "random": sum(1 for r in rd if r["k"] == 2)},
            "exact_condition_violations": sum(1 for r in sp if not r["identity_ok"]),
            "k_in_1_3_4_count": {"mersenne": sum(1 for r in sp if r["k"] in (1, 3, 4)),
                                 "random": sum(1 for r in rd if r["k"] in (1, 3, 4))},
            "n_rows": {"mersenne": len(sp), "random": len(rd)},
            "smallest_k": {"mersenne": sorted((r["k"], r["l"]) for r in sp)[:3],
                           "random": sorted((r["k"], r["l"]) for r in rd)[:3]}}


# ----------------------------------------------------------------------------
# part B: small ord_l(2) census against the index heuristic
# ----------------------------------------------------------------------------


def poisson_quantile(mean, q=0.999):
    if mean <= 0:
        return 0
    k, cdf, term = 0, 0.0, math.exp(-mean)
    cdf = term
    while cdf < q and k < 10 ** 6:
        k += 1
        term *= mean / k
        cdf += term
    return k


def small_ord_census(cells, D=10 ** 4, c0=3.0):
    out = []
    for cell in cells:
        cen = cell["census"]
        if cen["arm"] != "mersenne":
            continue
        rows = cen["rows"]
        if not rows:
            continue
        lmean = statistics.fmean(r["l"] for r in rows)
        mean_pred = c0 * len(rows) * D / lmean
        observed = sum(1 for r in rows if r["small_ord_l_2"])
        out.append({"p": cen["p"], "seed": cell["seed"], "n_rows": len(rows), "l_mean": lmean,
                    "predicted_mean_upper": mean_pred, "poisson_999_quantile": poisson_quantile(mean_pred),
                    "observed": observed, "within": observed <= max(poisson_quantile(mean_pred), 0),
                    "min_ord_l_2": min(r["ord_l_2"] for r in rows)})
    return out


# ----------------------------------------------------------------------------
# part C: deployed public curves (no secret scalar)
# ----------------------------------------------------------------------------

P256_P = 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1
P224_P = 2 ** 224 - 2 ** 96 + 1
P192_P = 2 ** 192 - 2 ** 64 - 1
DEPLOYED = [
    {"name": "P-521", "p": 2 ** 521 - 1, "form": "Mersenne 2^521 - 1 (c = 521)", "c": 521,
     "l": 0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409,
     "h": 1, "a": 2 ** 521 - 4,
     "b": 0x51953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00,
     "G": (0xC6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66,
           0x11839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650),
     "provenance": "EXP-ECDLP-6dacdb constants (aburan28/crypto src/ecc/curve_zoo.rs); verified here by [l]G = O"},
    {"name": "P-256", "p": P256_P, "form": "Solinas t^8 - t^7 + t^6 + t^3 - 1 at 2^32", "c": None,
     "l": 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551, "h": 1, "a": P256_P - 3,
     "b": 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
     "G": (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
           0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5),
     "provenance": "EXP-ECDLP-6dacdb constants; verified here by [l]G = O"},
    {"name": "P-224", "p": P224_P, "form": "Solinas t^7 - t^3 + 1 at 2^32", "c": None,
     "l": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFF16A2E0B8F03E13DD29455C5C2A3D, "h": 1, "a": P224_P - 3,
     "b": 0xB4050A850C04B3ABF54132565044B0B7D7BFD8BA270B39432355FFB4,
     "G": (0xB70E0CBD6BB4BF7F321390B94A03C1D356C21122343280D6115C1D21,
           0xBD376388B5F723FB4C22DFE6CD4375A05A07476444D5819985007E34),
     "provenance": "recalled FIPS 186-4 constants; verified here by [l]G = O, else reported as a constant error"},
    {"name": "P-192", "p": P192_P, "form": "Solinas t^3 - t - 1 at 2^64", "c": None,
     "l": 0xFFFFFFFFFFFFFFFFFFFFFFFF99DEF836146BC9B1B4D22831, "h": 1, "a": P192_P - 3,
     "b": 0x64210519E59C80E70FA7E9AB72243049FEB8DEECC146B9B1,
     "G": (0x188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012,
           0x07192B95FFC8DA78631011ED6B24CDD573F977A11E794811),
     "provenance": "recalled FIPS 186-4 constants; verified here by [l]G = O, else reported as a constant error"},
]


def part_c(cap):
    rows = []
    for cv in DEPLOYED:
        p, l, h = cv["p"], cv["l"], cv["h"]
        G = cv["G"]
        row = {"name": cv["name"], "form": cv["form"], "bits_p": p.bit_length(), "bits_l": l.bit_length(),
               "provenance": cv["provenance"], "p_prime": primeset.is_prime(p), "l_prime": primeset.is_prime(l),
               "hasse": abs(p + 1 - h * l) <= 2 * math.isqrt(p) + 1}
        on = (G[1] ** 2 - (G[0] ** 3 + cv["a"] * G[0] + cv["b"])) % p == 0
        row["base_point_on_curve"] = on
        row["order_check_lG_is_O"] = on and ec_mul(l, G, cv["a"], p) is None
        t0 = time.time()
        k = mult_order_capped(p, l, cap)
        row["ord_l_p"] = k if k else f"> {cap}"
        if cv["c"]:
            c = cv["c"]
            row["p_plus_1_is_power_of_2"] = (p + 1) & p == 0
            row["k_is_1"] = pow(2, c - 1, l) == 1              # l | 2^(c-1) - 1
            row["k_is_2"] = False                              # p + 1 = 2^c, l odd
            row["k_is_3"] = (pow(2, 2 * c, l) - pow(2, c, l) + 1) % l == 0
            row["k_is_4"] = (pow(2, 2 * c - 1, l) - pow(2, c, l) + 1) % l == 0
            row["k_in_1_to_4"] = row["k_is_1"] or row["k_is_3"] or row["k_is_4"]
        row["seconds"] = time.time() - t0
        rows.append(row)
        print(f"part C {cv['name']} done", file=sys.stderr, flush=True)
    return rows


# ----------------------------------------------------------------------------
# part D: modeled algebraic norms at p = 2^521 - 1 (no sieving)
# ----------------------------------------------------------------------------


def part_d(boxes_log2, samples, seed):
    p = 2 ** 521 - 1
    m = 2 ** 105
    assert 16 * p == m ** 5 - 16 and p == 2 ** 101 * m ** 4 - 1
    out = {"p": "2^521 - 1", "m": "2^105", "special": "x^5 - 16", "basem": "2^101 x^4 - 1",
           "shared_rational_side": "x - 2^105", "boxes": []}
    rng = random.Random(f"{EXP}:normbox:{seed}")
    for lb in boxes_log2:
        B = 1 << lb
        s_sp, s_bm = [], []
        for _ in range(samples):
            a = rng.randrange(-B, B + 1)
            b = rng.randrange(1, B + 1)
            if math.gcd(a, b) != 1:
                continue
            fs = abs(a ** 5 - 16 * b ** 5)
            fb = abs(2 ** 101 * a ** 4 - b ** 4)
            if fs == 0 or fb == 0:
                continue
            s_sp.append(math.log2(fs))
            s_bm.append(math.log2(fb))
        gap = statistics.fmean(s_sp) - statistics.fmean(s_bm)
        out["boxes"].append({"log2_B": lb, "n": len(s_sp), "mean_log2_norm_special": statistics.fmean(s_sp),
                             "mean_log2_norm_basem": statistics.fmean(s_bm), "gap_bits_special_minus_basem": gap,
                             "derived_prediction": -(97 - lb), "within_3_bits": abs(gap + (97 - lb)) <= 3})
    return out


# ----------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", nargs="+", default=["A", "B", "C", "D"])
    ap.add_argument("--c", type=int, nargs="+", default=[13, 17, 19, 31])
    ap.add_argument("--curves", type=int, default=64)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--exact-limit", type=int, default=1 << 20)
    ap.add_argument("--cap", type=int, default=10 ** 6)
    ap.add_argument("--boxes", type=int, nargs="+", default=[20, 30, 40])
    ap.add_argument("--norm-samples", type=int, default=100000)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()
    raw = {"experiment_id": EXP, "hypothesis_id": HYP, "argv": sys.argv}
    if "A" in args.part or "B" in args.part:
        cells = []
        for seed in args.seeds:
            for c in args.c:
                p = 2 ** c - 1
                assert primeset.is_prime(p), c
                cells.append({"c": c, "seed": seed, "census": census(p, "mersenne", c, args.curves, seed, args.exact_limit)})
                rp = primeset.matched_random_prime(c, seed, f"mersenne-c{c}")
                cells.append({"c": c, "seed": seed, "random_prime": rp,
                              "census": census(rp["p"], "random", None, args.curves, seed, args.exact_limit)})
                print(f"part A c={c} seed={seed} done", file=sys.stderr, flush=True)
        raw["part_a"] = {"cells": cells, "tests_per_seed": {str(s): arm_tests([x for x in cells if x["seed"] == s], s)
                                                            for s in args.seeds},
                         "tests_pooled": arm_tests(cells, args.seeds[0]),
                         "supersingular_controls": [{"p": x["census"]["p"], "arm": x["census"]["arm"],
                                                     **x["census"]["supersingular_control"]}
                                                    for x in cells if "supersingular_control" in x["census"]]}
        if "B" in args.part:
            raw["part_b"] = {"D": 10 ** 4, "c0": 3.0, "cells": small_ord_census(cells)}
    if "C" in args.part:
        raw["part_c"] = {"cap": args.cap, "rows": part_c(args.cap)}
    if "D" in args.part:
        raw["part_d"] = part_d(args.boxes, args.norm_samples, args.seeds[0])
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

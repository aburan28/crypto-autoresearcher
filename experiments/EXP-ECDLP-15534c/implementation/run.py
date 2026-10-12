#!/usr/bin/env python3
"""EXP-ECDLP-15534c: formal-group defect uniformity under three point-lift rules.

Smart's formal-group logarithm on E(Z/p^r): for P of odd prime order l and
Q = [k]P, lift both points by a rule L, compute [l]L(P), [l]L(Q) in Jacobian
coordinates, take z = -X Z / Y, and record delta = (z_Q/z_P - k) mod p after
removing the common p-power. Anomalous curves (l = p) are the positive
control where delta = 0 and k is recovered. Pure Python 3 standard library.
Observations only.
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


# ----------------------------------------------------------------------------
# F_p affine arithmetic and point counting (toy sizes)
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


def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R


def count_points(p, a, b):
    table = [0] * p
    for y in range(p):
        table[y * y % p] = 1
    total = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v:
            total += 1 if table[v] else -1
    return total


def factor_small(n):
    f = {}
    q = 2
    while q * q <= n:
        while n % q == 0:
            f[q] = f.get(q, 0) + 1
            n //= q
        q += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def sqrt_mod(n, p):
    if n == 0:
        return 0
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
        v = (x ** 3 + a * x + b) % p
        if v == 0:
            continue
        if pow(v, (p - 1) // 2, p) == 1:
            return (x, sqrt_mod(v, p))


# ----------------------------------------------------------------------------
# Z/p^r Jacobian-coordinate arithmetic
# ----------------------------------------------------------------------------

def jac_double(P, a, N):
    X, Y, Z = P
    XX = X * X % N
    YY = Y * Y % N
    YYYY = YY * YY % N
    ZZ = Z * Z % N
    S = 2 * ((X + YY) ** 2 - XX - YYYY) % N
    M = (3 * XX + a * ZZ * ZZ) % N
    T = (M * M - 2 * S) % N
    Y3 = (M * (S - T) - 8 * YYYY) % N
    Z3 = ((Y + Z) ** 2 - YY - ZZ) % N
    return (T, Y3, Z3)


def jac_add(P, Q, N):
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    Z1Z1 = Z1 * Z1 % N
    Z2Z2 = Z2 * Z2 % N
    U1 = X1 * Z2Z2 % N
    U2 = X2 * Z1Z1 % N
    S1 = Y1 * Z2 * Z2Z2 % N
    S2 = Y2 * Z1 * Z1Z1 % N
    H = (U2 - U1) % N
    I = (2 * H) ** 2 % N
    J = H * I % N
    r = 2 * (S2 - S1) % N
    V = U1 * I % N
    X3 = (r * r - J - 2 * V) % N
    Y3 = (r * (V - X3) - 2 * S1 * J) % N
    Z3 = (((Z1 + Z2) ** 2 - Z1Z1 - Z2Z2) * H) % N
    return (X3, Y3, Z3)


def jac_mul(k, P, a, N):
    """Left-to-right double-and-add; the caller guarantees that only the final
    addition can be degenerate (P1 = -P2 mod p), which is the formal-group step."""
    bits = bin(k)[3:]
    R = P
    for bit in bits:
        R = jac_double(R, a, N)
        if bit == "1":
            R = jac_add(R, P, N)
    return R


def hensel_y(xh, y0, a, b, p, r):
    """Lift y0 (y0^2 = f(xh) mod p, y0 != 0) to a root mod p^r by Newton."""
    N = p ** r
    y = y0 % N
    for _ in range(r.bit_length() + 1):
        fy = (y * y - (xh ** 3 + a * xh + b)) % N
        y = (y - fy * pow(2 * y, -1, N)) % N
    assert (y * y - (xh ** 3 + a * xh + b)) % N == 0
    return y


def vp(n, p):
    if n == 0:
        return None
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def formal_z(R, p, N):
    X, Y, Z = R
    assert Z % p == 0 and Y % p != 0, "CTRL-REDUCTION failed"
    return (-X * Z * pow(Y, -1, N)) % N


def lift_point(rule, P, a, b, p, r, rng):
    x, y = P
    N = p ** r
    if rule == "L1_integer_hensel":
        xh = x
    elif rule == "L2_teichmuller_hensel":
        xh = pow(x, p ** (r - 1), N)
        if x:
            assert pow(xh, p - 1, N) == 1, "CTRL-TEICHMULLER failed"
    elif rule == "L3_random_hensel":
        xh = (x + p * rng.randrange(p ** (r - 1))) % N
    else:
        raise ValueError(rule)
    # lifted a, b are the integer representatives (the lifted model is fixed per curve)
    yh = hensel_y(xh, y, a, b, p, r)
    return (xh, yh, 1)


def defect(rule, P, Q, k, l, a, b, p, r, rng):
    N = p ** r
    Ph = lift_point(rule, P, a, b, p, r, rng)
    Qh = lift_point(rule, Q, a, b, p, r, rng)
    zP = formal_z(jac_mul(l, Ph, a, N), p, N)
    zQ = formal_z(jac_mul(l, Qh, a, N), p, N)
    vP, vQ = vp(zP, p), vp(zQ, p)
    if vP is None or vQ is None or vP != 1 or vQ != 1:
        return {"vP": vP, "vQ": vQ, "delta": None}
    ratio = (zQ // p) * pow(zP // p, -1, p) % p
    return {"vP": vP, "vQ": vQ, "delta": (ratio - k) % p, "ratio": ratio}


# ----------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------

def gammq(a, x):
    """Regularized upper incomplete gamma Q(a, x) (Numerical Recipes)."""
    if x < a + 1:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(500):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    b, c, d = x + 1 - a, 1e300, 1 / (x + 1 - a)
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def uniformity(deltas, p, bins=20):
    n = len(deltas)
    if n == 0:
        return None
    h = [0] * bins
    for dlt in deltas:
        h[min(bins - 1, dlt * bins // p)] += 1
    e = n / bins
    chi = sum((c - e) ** 2 / e for c in h)
    pval = gammq((bins - 1) / 2, chi / 2)
    xs = sorted(d / p for d in deltas)
    ks = max(max(abs((i + 1) / n - x), abs(x - i / n)) for i, x in enumerate(xs))
    return {"n": n, "histogram": h, "chi_square": chi, "chi_square_p_value": pval,
            "ks_distance": ks, "ks_threshold_alpha_0_001": 1.949 / math.sqrt(n),
            "zero_count": sum(1 for d in deltas if d == 0)}


# ----------------------------------------------------------------------------
# cells
# ----------------------------------------------------------------------------

RULES = ["L1_integer_hensel", "L2_teichmuller_hensel", "L3_random_hensel"]


def curve_with_large_prime_factor(p, rng, min_l):
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            continue
        n = count_points(p, a, b)
        if n == p:
            continue
        l = max(factor_small(n))
        if l >= min_l and l % 2 == 1 and l != p:
            return a, b, n, l


def point_of_order(p, a, b, n, l, rng):
    while True:
        R = random_point(p, a, b, rng)
        P = ec_mul(n // l, R, a, p)
        if P is not None:
            assert ec_mul(l, P, a, p) is None
            return P


def run_prime(p, arm, curves, draws, seed, r, precision_check):
    rng = random.Random(f"EXP-ECDLP-15534c:{seed}:{arm}:{p}")
    out = {"p": p, "arm": arm, "curves": []}
    for _ in range(curves):
        a, b, n, l = curve_with_large_prime_factor(p, rng, 2 ** 8)
        P = point_of_order(p, a, b, n, l, rng)
        crow = {"a": a, "b": b, "order": n, "l": l, "P": P, "rules": {}}
        for rule in RULES:
            deltas, skipped, prec_mismatch = [], 0, 0
            draw_log = []  # (k, delta) per draw, in draw order, for independent replay
            drng = random.Random(f"EXP-ECDLP-15534c:{seed}:{arm}:{p}:{a}:{b}:{rule}")
            for i in range(draws):
                k = drng.randrange(1, l)
                Q = ec_mul(k, P, a, p)
                res = defect(rule, P, Q, k, l, a, b, p, r, drng)
                if res["delta"] is None:
                    skipped += 1
                    draw_log.append([k, None])
                    continue
                deltas.append(res["delta"])
                draw_log.append([k, res["delta"]])
                if precision_check and i % 10 == 0:
                    res8 = defect(rule, P, Q, k, l, a, b, p, r + 2,
                                  random.Random(f"prec:{seed}:{i}"))
                    if rule != "L3_random_hensel" and res8["delta"] != res["delta"]:
                        prec_mismatch += 1
            crow["rules"][rule] = {"uniformity": uniformity(deltas, p), "higher_valuation_skipped": skipped,
                                   "precision_mismatch": prec_mismatch, "draws": draw_log,
                                   "precision": r}
        out["curves"].append(crow)
        print(f"{arm} p={p} curve a={a} b={b} l={l} done", file=sys.stderr, flush=True)
    return out


def anomalous_control(bits_lo, bits_hi, seed, draws, r, arm_kind, d=None):
    """Find an anomalous curve on a prime of the given arm kind and run Smart's attack."""
    rng = random.Random(f"EXP-ECDLP-15534c:anomalous:{seed}:{arm_kind}")
    tried = 0
    while True:
        if arm_kind == "special":
            cands = primeset.special_primes(d, rng.randrange(bits_lo, bits_hi + 1), 3)
            if not cands:
                continue
            p = rng.choice(cands)["p"]
        else:
            p = primeset.matched_random_prime(rng.randrange(bits_lo, bits_hi + 1), seed, f"anom{tried}")["p"]
        for _ in range(400):
            tried += 1
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b ** 2) % p == 0:
                continue
            if count_points(p, a, b) == p:
                P = random_point(p, a, b, rng)
                results = {}
                for rule in RULES:
                    ok = 0
                    zeros = 0
                    for i in range(draws):
                        k = rng.randrange(1, p)
                        Q = ec_mul(k, P, a, p)
                        res = defect(rule, P, Q, k, p, a, b, p, r, rng)
                        if res["delta"] == 0:
                            zeros += 1
                        if res.get("ratio") == k:
                            ok += 1
                    results[rule] = {"recovered": ok, "delta_zero": zeros, "draws": draws}
                return {"p": p, "a": a, "b": b, "curves_tried": tried, "results": results,
                        "pass": all(v["recovered"] == draws for v in results.values())}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", type=int, nargs="+", default=[2, 3, 5])
    ap.add_argument("--bits", type=int, default=14)
    ap.add_argument("--primes-per-d", type=int, default=2)
    ap.add_argument("--curves", type=int, default=6)
    ap.add_argument("--draws", type=int, default=400)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--precision", type=int, default=6)
    ap.add_argument("--anomalous-draws", type=int, default=50)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()
    raw = {"experiment_id": "EXP-ECDLP-15534c", "hypothesis_id": "H-ECDLP-bd1572", "argv": sys.argv,
           "cells": [], "anomalous_controls": {}}
    raw["anomalous_controls"]["special"] = anomalous_control(11, 13, args.seeds[0], args.anomalous_draws,
                                                            args.precision, "special", d=args.d[0])
    raw["anomalous_controls"]["random"] = anomalous_control(11, 13, args.seeds[0], args.anomalous_draws,
                                                           args.precision, "random")
    print("anomalous controls done", file=sys.stderr, flush=True)
    for seed in args.seeds:
        for d in args.d:
            for i, sp in enumerate(primeset.special_primes(d, args.bits, args.primes_per_d)):
                raw["cells"].append({"d": d, "seed": seed, "special": sp,
                                     "census": run_prime(sp["p"], "special", args.curves, args.draws, seed,
                                                         args.precision, True)})
                rp = primeset.matched_random_prime(args.bits, seed, f"d{d}:{i}")
                raw["cells"].append({"d": d, "seed": seed, "random": rp,
                                     "census": run_prime(rp["p"], "random", args.curves, args.draws, seed,
                                                         args.precision, True)})
    # summary: rejections at alpha = 0.001 with Bonferroni over all cells
    tests = [(c["census"]["arm"], rule, cr["rules"][rule]["uniformity"])
             for c in raw["cells"] for cr in c["census"]["curves"] for rule in RULES]
    m = max(1, len(tests))
    rejections = [{"arm": arm, "rule": rule, "chi_p": u["chi_square_p_value"], "ks": u["ks_distance"]}
                  for arm, rule, u in tests if u and (u["chi_square_p_value"] < 0.001 / m
                                                    or u["ks_distance"] > 1.949 / math.sqrt(u["n"]) * math.sqrt(1 + math.log(m)))]
    raw["summary"] = {"tests": len(tests), "bonferroni_alpha": 0.001 / m, "rejections": rejections,
                      "rejections_per_rule_arm": {f"{arm}:{rule}": sum(1 for r in rejections if r["arm"] == arm and r["rule"] == rule)
                                                  for arm in ("special", "random") for rule in RULES}}
    raw["wall_clock_seconds"] = time.time() - started
    raw_path = os.path.join(args.out, "raw-result.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True, default=str)
    src = os.path.abspath(__file__)
    manifest = {"experiment_id": "EXP-ECDLP-15534c", "command": " ".join(sys.argv),
                "python": platform.python_version(), "platform": platform.platform(),
                "source_sha256": {"run.py": hashlib.sha256(open(src, "rb").read()).hexdigest(),
                                  "primeset.py": hashlib.sha256(open(os.path.join(os.path.dirname(src), "primeset.py"), "rb").read()).hexdigest()},
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

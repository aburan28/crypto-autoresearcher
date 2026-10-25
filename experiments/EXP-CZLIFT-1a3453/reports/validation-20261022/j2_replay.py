#!/usr/bin/env python3
"""Independent replay of EXP-CZLIFT-1a3453 curves (TASK-20261022-8ebef8, J2).

Shares with the producer only (i) the rng consumption protocol of
measure_curve (needed to land on the same generator P, permutation and
uniform draws) and (ii) sympy.sqrt_mod's root convention used by
toycurve.lift_x.  Everything else is independent:
  * F_p arithmetic written here;
  * the torsion lift T1 = s_tor(P) is found by Newton iteration on
    h(x) = x([n-1]T(x)) - x  (h ~ -n (x - x1) to first order), entirely in
    affine coordinates over Z/p^K with unit denominators (no formal-group
    arithmetic, unlike the producer's T = P^ - [n^-1]([n]P^)), then certified
    by [n-1]T1 == -T1 mod p^K;
  * s_tor([k]P) = [k]T1 by successive affine addition (homomorphism), certified
    by [n-1]T1 == -T1 at the end of the chain;
  * the spectrum is the vectorised (p-1) x n FFT from blind/blind_derivation.py.
Records per row: max_power, above, argmax (a, t), for real, shuffled and
uniform series, plus digit-multiplicity statistics on the half range.
Usage: j2_replay.py OUT.json RUN_DIR[:idx,idx,...|all] ...
"""
from __future__ import annotations

import json
import math
import random
import sys
import time

import numpy as np
import sympy

K = 5
MARGIN = 12.0


# ---------------- F_p ----------------
def fp_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def fp_mul(k, P, a, p):
    R = None
    A = P
    while k:
        if k & 1:
            R = fp_add(R, A, a, p)
        A = fp_add(A, A, a, p)
        k >>= 1
    return R


def fp_lift_x(x, a, b, p):
    rhs = (x * x * x + a * x + b) % p
    if rhs == 0:
        return (x % p, 0)
    if pow(rhs, (p - 1) // 2, p) != 1:
        return None
    r = sympy.ntheory.residue_ntheory.sqrt_mod(rhs, p)
    return None if r is None else (x % p, int(r))


def protocol_point(a, b, p, n, h, rng):
    while True:
        while True:
            x = rng.randrange(p)
            P = fp_lift_x(x, a, b, p)
            if P is not None and P[1] != 0:
                if rng.random() < 0.5:
                    P = (P[0], (-P[1]) % p)
                break
        P = fp_mul(h, P, a, p)
        if P is not None and P[1] != 0 and fp_mul(n, P, a, p) is None:
            return P


# ---------------- Z/p^K affine ----------------
def zp_add(P, Q, A, M, p):
    """Affine addition over Z/M, M = p^K; requires unit denominators."""
    x1, y1 = P
    x2, y2 = Q
    if (x1 - x2) % p == 0:
        if (y1 - y2) % p == 0 and (x1 - x2) % M == 0 and (y1 - y2) % M == 0:
            lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, M) % M
        else:
            raise ArithmeticError("non-unit denominator")
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, M) % M
    x3 = (lam * lam - x1 - x2) % M
    return (x3, (lam * (x1 - x3) - y1) % M)


def zp_mul(k, P, A, M, p):
    """[k]P for 1 <= k < n (all partial multiples reduce to finite points)."""
    R = None
    D = P
    while k:
        if k & 1:
            R = D if R is None else zp_add(R, D, A, M, p)
        k >>= 1
        if k:
            D = zp_add(D, D, A, M, p)
    return R


def y_from_x(x, y0, A, B, M, p):
    f = (x ** 3 + A * x + B) % M
    y = y0 % M
    for _ in range(K + 2):
        y = (y - (y * y - f) * pow(2 * y, -1, M)) % M
    assert (y * y - f) % M == 0 and (y - y0) % p == 0
    return y


def torsion_lift(P, A, B, n, p):
    M = p ** K
    x0, y0 = P
    x = x0
    for _ in range(8):
        T = (x, y_from_x(x, y0, A, B, M, p))
        Q = zp_mul(n - 1, T, A, M, p)
        hx = (Q[0] - x) % M
        if hx == 0 and (Q[1] + T[1]) % M == 0:
            return T
        x = (x + hx * pow(n, -1, M)) % M
    raise ArithmeticError("Newton did not converge")


def digits(v, p):
    out = []
    for _ in range(K):
        out.append(v % p)
        v //= p
    return out


# ---------------- spectrum ----------------
def spectrum(f_full, p, n):
    m = (n - 1) // 2
    T = math.log((p - 1) * n) + MARGIN
    d = np.asarray(f_full[1:m + 1], dtype=np.int64)
    a = np.arange(1, p, dtype=np.int64)[:, None]
    z = np.zeros((p - 1, n), dtype=np.complex128)
    z[:, 1:m + 1] = np.exp(2j * np.pi * ((a * d[None, :]) % p) / p)
    X = np.abs(np.fft.fft(z, axis=1)) ** 2 / m
    ia, it = np.unravel_index(int(X.argmax()), X.shape)
    return float(X.max()), int((X > T).sum()), T, int(ia) + 1, int(it)


def replay_curve(c, seed):
    p, A, B, N, n = c["p"], c["A"], c["B"], c["N"], c["n"]
    a, b = A % p, B % p
    h = N // n
    rng = random.Random(seed * 104_729 + p * 17 + (A % p))
    P = protocol_point(a, b, p, n, h, rng)
    for _ in range(1, n):
        rng.randrange(p)                       # producer's Hensel eps draws
    perm = np.array(rng.sample(range(n), n))
    M = p ** K
    T1 = torsion_lift(P, A % M, B % M, n, p)
    xs = np.zeros((K, n), dtype=np.int64)
    ys = np.zeros((K, n), dtype=np.int64)
    R = T1
    for k in range(1, n):
        if k > 1:
            R = zp_add(R, T1, A % M, M, p)
        assert (R[0] % p, R[1] % p) == fp_mul(k, P, a, p)
        for i, dgt in enumerate(digits(R[0], p)):
            xs[i, k] = dgt
        for i, dgt in enumerate(digits(R[1], p)):
            ys[i, k] = dgt
    assert R[0] == T1[0] and (R[1] + T1[1]) % M == 0     # [n-1]T1 = -T1
    m = (n - 1) // 2
    rows = []
    for coord, arr in (("x", xs), ("y", ys)):
        for i in range(K):
            f = arr[i]
            r_mp, r_ab, T, r_a, r_t = spectrum(f, p, n)
            s_mp, s_ab, _, s_a, s_t = spectrum(f[perm], p, n)
            uni = np.array([rng.randrange(p) for _ in range(n)], dtype=np.int64)
            u_mp, u_ab, _, u_a, u_t = spectrum(uni, p, n)
            half = f[1:m + 1]
            vals, cnt = np.unique(half, return_counts=True)
            rows.append({"coord": coord, "digit": i, "threshold": T,
                         "max_power": r_mp, "above": r_ab, "argmax_a": r_a, "argmax_t": r_t,
                         "shuffled_max_power": s_mp, "shuffled_above": s_ab,
                         "shuffled_argmax_t": s_t,
                         "uniform_max_power": u_mp, "uniform_above": u_ab,
                         "half_distinct_values": int(len(vals)), "half_max_multiplicity": int(cnt.max()),
                         "half_len": m,
                         "shuffled_half_contains_k0_placeholder": bool(0 in set(perm[1:m + 1].tolist()))})
    return {"P": list(P), "T1": [int(T1[0]), int(T1[1])], "rows": rows}


def compare(rec_rows, my_rows):
    worst = 0.0
    mism = []
    key = {(r["coord"], r["digit"]): r for r in rec_rows}
    for r in my_rows:
        q = key[(r["coord"], r["digit"])]
        for f in ("max_power", "shuffled_max_power", "uniform_max_power", "threshold"):
            d = abs(r[f] - q[f]) / max(1.0, abs(q[f]))
            worst = max(worst, d)
            if d > 1e-9:
                mism.append((r["coord"], r["digit"], f, q[f], r[f]))
        for f in ("above", "shuffled_above", "uniform_above"):
            if r[f] != q[f]:
                mism.append((r["coord"], r["digit"], f, q[f], r[f]))
    return worst, mism


def main():
    out_path = sys.argv[1]
    results = []
    for spec in sys.argv[2:]:
        run_dir, _, sel = spec.partition(":")
        raw = json.load(open(run_dir + "/raw-result.json"))
        seed = raw["metrics"]["seed"]
        curves = raw["raw"]["curves"]
        idx = range(len(curves)) if sel in ("", "all") else [int(s) for s in sel.split(",")]
        for i in idx:
            c = curves[i]
            t0 = time.time()
            rep = replay_curve(c, seed)
            worst, mism = compare(c["rows"], rep["rows"])
            results.append({"run": run_dir.rstrip("/").split("/")[-1], "seed": seed, "index": i,
                            "arm": c["arm"], "label": c["label"], "p": c["p"], "n": c["n"], "N": c["N"],
                            "seconds": round(time.time() - t0, 2), "worst_rel_diff": worst,
                            "mismatches": mism, "replay": rep})
            print(f"{results[-1]['run']} #{i:2d} {c['arm']:13s} {c['label']:7s} p={c['p']:3d} n={c['n']:3d} "
                  f"worst={worst:.2e} mism={len(mism)} {results[-1]['seconds']}s", flush=True)
    json.dump(results, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main()

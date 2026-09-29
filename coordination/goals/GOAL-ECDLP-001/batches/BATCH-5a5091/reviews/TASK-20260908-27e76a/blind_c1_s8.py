#!/usr/bin/env python3
"""Blind Stage 8 C1 re-derivation from v1_stage8_protocol cells only.

Does not import or read the Stage 8 producer or its raw result.
Lagrange to monomial basis over F_p (T2) and Z/N (T1).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
_ = ROOT  # workspace root; cells are hardcoded, no producer import

P = 16777213
D = 20
T2 = {
    "a": 19,
    "b": 107,
    "N": 16777213,
    "P": (0, 1722727),
    "V": [0, 14386069, 13311471, 510744, 13641516, 11286066, 16703438, 13064901, 3436861, 9847978, 4422270, 2431989, 8626592, 2704728, 8015097, 11447766, 8129445, 341717, 16207358, 12600408],
}
T1 = {
    "a": 0,
    "b": 7,
    "N": 16770451,
    "P": (6, 7827705),
    "V": [6, 4288347, 2837810, 15061002, 7941042, 3891067, 6883471, 15571429, 15172588, 6789969, 6889484, 865709, 4039235, 6596143, 14029655, 5242584, 7908075, 2872040, 4197418, 1510565],
}


def add(p: int, a: int, P1, Q):
    if P1 is None:
        return Q
    if Q is None:
        return P1
    x1, y1 = P1
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P1 == Q:
        if y1 == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def confirm_V(cell: dict) -> None:
    R = None
    for k in range(1, D + 1):
        R = add(P, cell["a"], R, cell["P"])
        if R is None or R[0] != cell["V"][k - 1]:
            raise RuntimeError(f"V mismatch or O at k={k}")


def poly_mul(p: list[int], q: list[int], mod: int) -> list[int]:
    out = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a == 0:
            continue
        for j, b in enumerate(q):
            if b == 0:
                continue
            out[i + j] = (out[i + j] + a * b) % mod
    return out


def poly_scale(p: list[int], s: int, mod: int) -> list[int]:
    return [(c * s) % mod for c in p]


def poly_add(p: list[int], q: list[int], mod: int) -> list[int]:
    n = max(len(p), len(q))
    out = [0] * n
    for i in range(n):
        a = p[i] if i < len(p) else 0
        b = q[i] if i < len(q) else 0
        out[i] = (a + b) % mod
    return out


def lagrange_monomial(xs: list[int], ys: list[int], mod: int) -> list[int]:
    n = len(xs)
    coeffs = [0]
    for i in range(n):
        basis = [1]
        denom = 1
        for j in range(n):
            if i == j:
                continue
            basis = poly_mul(basis, [(-xs[j]) % mod, 1], mod)
            denom = (denom * ((xs[i] - xs[j]) % mod)) % mod
        scale = (ys[i] * pow(denom, -1, mod)) % mod
        coeffs = poly_add(coeffs, poly_scale(basis, scale, mod), mod)
    while len(coeffs) < D:
        coeffs.append(0)
    if len(coeffs) > D:
        raise RuntimeError("interpolant degree >= D")
    for i, x in enumerate(xs):
        acc = 0
        xp = 1
        for c in coeffs:
            acc = (acc + c * xp) % mod
            xp = (xp * x) % mod
        if acc != ys[i] % mod:
            raise RuntimeError(f"recovery failed at i={i}")
    return coeffs[:D]


def degree_nnz(coeffs: list[int]) -> tuple[int, int]:
    nnz = sum(1 for c in coeffs if c != 0)
    deg = -1
    for j in range(len(coeffs) - 1, -1, -1):
        if coeffs[j] != 0:
            deg = j
            break
    return deg, nnz


def main() -> int:
    confirm_V(T2)
    confirm_V(T1)
    ks = list(range(1, D + 1))
    t2_c = lagrange_monomial(T2["V"], ks, T2["N"])
    t1_c = lagrange_monomial(T1["V"], ks, T1["N"])
    k_null = ks[:]
    random.Random(20260908).shuffle(k_null)
    n2_c = lagrange_monomial(T1["V"], k_null, T1["N"])
    t2_d, t2_n = degree_nnz(t2_c)
    t1_d, t1_n = degree_nnz(t1_c)
    n2_d, n2_n = degree_nnz(n2_c)
    raw = {
        "T2_C1": {"degree": t2_d, "nnz": t2_n, "coefficients": t2_c},
        "T1_C1": {"degree": t1_d, "nnz": t1_n, "coefficients": t1_c},
        "T1_NULL2_C1": {
            "degree": n2_d,
            "nnz": n2_n,
            "coefficients": n2_c,
            "k_shuffled": k_null,
            "seed": 20260908,
        },
        "T2_C1_degree": t2_d,
        "T2_C1_nnz": t2_n,
        "T1_C1_degree": t1_d,
        "T1_C1_nnz": t1_n,
        "T1_NULL2_C1_degree": n2_d,
        "T1_NULL2_C1_nnz": n2_n,
        "expected_degree": 19,
        "expected_nnz": 20,
        "match_expected": t2_d == 19 and t2_n == 20 and t1_d == 19 and t1_n == 20 and n2_d == 19 and n2_n == 20,
        "T2_C1_high_degree_is_not_failed_infrastructure": True,
        "C1_miss_is_not_H1_closure": True,
        "not_an_H1_claim": True,
        "SMALL_W_or_LARGE_W": False,
        "source": "frozen v1_stage8_protocol cells plus independent Lagrange",
        "producer_not_read": True,
        "ROOT_parents": 7,
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if raw["match_expected"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

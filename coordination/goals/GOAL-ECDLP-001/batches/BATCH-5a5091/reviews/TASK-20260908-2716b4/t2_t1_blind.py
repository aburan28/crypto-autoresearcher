#!/usr/bin/env python3
"""Blind Stage 4 re-derivation from v1_stage4_protocol cells only.

Does not import or read the Stage 4 producer or its raw result.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(ROOT / "experiments" / "EXP-ECDLP-bbb42f"))
from driver.projective_ecc import from_affine, proj_scalar_mult  # noqa: E402

P = 262139
D = 20
T2 = {
    "a": 106,
    "b": 13,
    "N": 262139,
    "P": (2, 200493),
    "V": [2, 1136, 251979, 209873, 144684, 42906, 240592, 176375, 184939, 157945, 75011, 138852, 247488, 234240, 255029, 200181, 114653, 218956, 229520, 262059],
}
T1 = {
    "a": 1,
    "b": 52,
    "N": 261439,
    "P": (3, 249411),
    "V": [3, 76720, 159789, 140040, 250531, 65927, 193243, 202502, 174467, 97932, 150254, 249184, 212315, 29553, 155044, 131285, 119861, 43011, 82732, 104615],
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


def multiples(cell: dict) -> list[tuple[int, tuple[int, int]]]:
    rows = []
    R = None
    for k in range(1, D + 1):
        R = add(P, cell["a"], R, cell["P"])
        if R is None or R[0] != cell["V"][k - 1]:
            raise RuntimeError(f"V mismatch or O at k={k}")
        rows.append((k, R))
    return rows


def recover_affine(xs: list[int], ks: list[int], n: int):
    x0, x1 = xs[0], xs[1]
    k0, k1 = ks[0], ks[1]
    dx = (x1 - x0) % n
    if dx == 0:
        return None, None, False
    a = ((k1 - k0) * pow(dx, -1, n)) % n
    b = (k0 - a * x0) % n
    exact = all((a * x + b) % n == k for x, k in zip(xs, ks))
    return a, b, exact


def hensel_lift_y(x: int, y: int, a: int, b: int, p: int) -> int:
    if y % p == 0:
        raise ValueError("y=0")
    rhs = x**3 + a * x + b
    diff = rhs - y * y
    if diff % p != 0:
        raise ValueError("not on curve")
    t = ((diff // p) * pow(2 * y, -1, p)) % p
    return (y + p * t) % (p * p)


def formal_log_s(x: int, y: int, a: int, b: int, p: int):
    n = p * p
    y_lift = hensel_lift_y(x, y, a, b, p)
    Rp = proj_scalar_mult(p, from_affine((x % n, y_lift), n), a % n, n)
    X, Y, Z = Rp
    if Y % p == 0:
        raise RuntimeError("Y not a unit")
    t = (-X * pow(Y, -1, n)) % n
    if t % p != 0:
        raise RuntimeError("t not 0 mod p")
    return (t // p) % p


def main() -> int:
    t2_rows = multiples(T2)
    ss, ks = [], []
    t2_inapplicable = 0
    for k, (x, y) in t2_rows:
        try:
            ss.append(formal_log_s(x, y, T2["a"], T2["b"], P))
            ks.append(k)
        except (RuntimeError, ValueError):
            t2_inapplicable += 1
    if t2_inapplicable or len(ss) != D:
        t2_a, t2_b, t2_exact = None, None, False
    else:
        t2_a, t2_b, t2_exact = recover_affine(ss, ks, T2["N"])

    t1_rows = multiples(T1)
    t1_vs = [R[0] for _, R in t1_rows]
    t1_ks = [k for k, _ in t1_rows]
    t1_a, t1_b, t1_exact = recover_affine(t1_vs, t1_ks, T1["N"])

    t1_formal_ok = 0
    for k, (x, y) in t1_rows:
        try:
            formal_log_s(x, y, T1["a"], T1["b"], P)
            t1_formal_ok += 1
        except (RuntimeError, ValueError):
            pass

    raw = {
        "T2_formal_log": {
            "applicable_rows": D - t2_inapplicable,
            "recovers_exact_affine": t2_exact,
            "a_hat": t2_a,
            "b_hat": t2_b,
        },
        "T1_identity": {
            "recovers_exact_affine": t1_exact,
            "a_hat": t1_a,
            "b_hat": t1_b,
        },
        "T1_formal_log_applicable_rows": t1_formal_ok,
        "T2_formal_log_holds": bool(t2_exact),
        "T1_identity_is_not_a_hard_gate": True,
        "not_an_H1_claim": True,
        "SMALL_W_or_LARGE_W": False,
        "source": "frozen v1_stage4_protocol cells plus protocol formal-log formula",
        "producer_not_read": True,
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if raw["T2_formal_log_holds"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

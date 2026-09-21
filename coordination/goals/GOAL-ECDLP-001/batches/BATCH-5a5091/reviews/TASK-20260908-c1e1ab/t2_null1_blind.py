#!/usr/bin/env python3
"""Blind Stage 1 re-derivation from v1_stage1_protocol cells only.

Does not import or read the Stage 1 producer or its raw result.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(ROOT / "experiments" / "EXP-ECDLP-bbb42f"))
from driver.projective_ecc import from_affine, proj_scalar_mult  # noqa: E402

P = 523
D = 20
T2 = {
    "a": 2,
    "b": 6,
    "N": 523,
    "P": (0, 23),
    "V": [0, 436, 365, 181, 65, 502, 497, 417, 473, 485, 5, 500, 158, 362, 185, 419, 237, 340, 29, 42],
}
NULL1 = {
    "a": 3,
    "b": 3,
    "N": 503,
    "P": (1, 141),
    "V": [1, 74, 512, 87, 98, 95, 425, 377, 392, 240, 85, 171, 219, 346, 361, 278, 197, 374, 262, 239],
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

    n1_rows = multiples(NULL1)
    n1_vs = [R[0] for _, R in n1_rows]
    n1_ks = [k for k, _ in n1_rows]
    n1_a, n1_b, n1_exact = recover_affine(n1_vs, n1_ks, NULL1["N"])

    n1_formal_ok = 0
    for k, (x, y) in n1_rows:
        try:
            formal_log_s(x, y, NULL1["a"], NULL1["b"], P)
            n1_formal_ok += 1
        except (RuntimeError, ValueError):
            pass

    raw = {
        "T2_formal_log": {
            "applicable_rows": D - t2_inapplicable,
            "recovers_exact_affine": t2_exact,
            "a_hat": t2_a,
            "b_hat": t2_b,
        },
        "NULL1_identity": {
            "recovers_exact_affine": n1_exact,
            "a_hat": n1_a,
            "b_hat": n1_b,
        },
        "NULL1_formal_log_applicable_rows": n1_formal_ok,
        "fixture_pass": bool(t2_exact) and (n1_exact is False),
        "not_an_H1_claim": True,
        "SMALL_W_or_LARGE_W": False,
        "source": "frozen v1_stage1_protocol cells plus protocol formal-log formula",
        "producer_not_read": True,
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if raw["fixture_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

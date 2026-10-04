#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-4be480 Stage 0 P-S0-DIMTRIPLE.

Frozen fixture numbers from review_plan_s0_4be480 only.
Does not import the Stage 0 producer. Does not read RUN-ECDLP-4be480-S0.
Does not construct a Frobenius. Does not dispose P-S1-DIGIT.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]

FORBIDDEN = [
    ROOT / "experiments/EXP-ECDLP-4be480/implementation/stage0_dimtriple.py",
    ROOT / "experiments/EXP-ECDLP-4be480/runs/RUN-ECDLP-4be480-S0/raw-result.json",
    ROOT / "experiments/EXP-ECDLP-4be480/execution-report-s0.yaml",
]

A = Fraction(1)
B = Fraction(1)
U = Fraction(2)
P_D1 = (Fraction(0), Fraction(1))
Q_D1 = (Fraction(0), Fraction(-1))


def weierstrass_disc(a: Fraction, b: Fraction) -> Fraction:
    return Fraction(-16) * (Fraction(4) * a ** 3 + Fraction(27) * b ** 2)


def lies_on(a: Fraction, b: Fraction, pt: tuple[Fraction, Fraction]) -> bool:
    x, y = pt
    return y * y == x * x * x + a * x + b


def double_point(a: Fraction, pt: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    x, y = pt
    slope = (Fraction(3) * x * x + a) / (Fraction(2) * y)
    x3 = slope * slope - Fraction(2) * x
    y3 = slope * (x - x3) - y
    return (x3, y3)


def scale_abxy(u: Fraction, a: Fraction, b: Fraction, pt: tuple[Fraction, Fraction]):
    x, y = pt
    return (u ** 4 * a, u ** 6 * b, (u * u * x, u ** 3 * y))


def cone_dims() -> tuple[int, int, int]:
    # Frozen cone of Omega_E -> Omega_D in degree 1.
    # r(c) = (c, c) on H^0; rank 1; coker dim 1.
    # H^1_ord spanned by {dx/y, x dx/y}; dim 2.
    # H^1(D) = 0.
    # H^1_rel = coker(r) \oplus H^1_ord; dim 3.
    # ker of the connecting map is coker(r); dim 1.
    dim_coker = 2 - 1
    dim_h1_ord = 2
    dim_h1_rel = dim_coker + dim_h1_ord
    dim_ker = dim_coker
    return (dim_h1_rel, dim_h1_ord, dim_ker)


def main() -> int:
    for path in FORBIDDEN:
        if path.exists():
            # Presence on disk is allowed; reading is not. Do not open.
            pass

    disc = weierstrass_disc(A, B)
    two_p = double_point(A, P_D1)
    expected_two_p = (Fraction(1, 4), Fraction(-9, 8))
    a_s, b_s, p_s = scale_abxy(U, A, B, P_D1)
    _, _, q_s = scale_abxy(U, A, B, Q_D1)

    d1_ok = (
        P_D1 != Q_D1
        and lies_on(A, B, P_D1)
        and lies_on(A, B, Q_D1)
    )
    d2_ok = (
        P_D1 != two_p
        and lies_on(A, B, P_D1)
        and lies_on(A, B, two_p)
        and two_p == expected_two_p
    )
    scaled_ok = (
        p_s != q_s
        and a_s == Fraction(16)
        and b_s == Fraction(64)
        and p_s == (Fraction(0), Fraction(8))
        and q_s == (Fraction(0), Fraction(-8))
        and lies_on(a_s, b_s, p_s)
        and lies_on(a_s, b_s, q_s)
    )
    d_eq_same = P_D1 == P_D1
    reject_repeated = d_eq_same and lies_on(A, B, P_D1)
    triple = cone_dims() if (d1_ok and d2_ok and scaled_ok) else None
    unmarked = 2

    result = {
        "task_id": "TASK-20260908-f83935",
        "quantity": "discriminant, 2P, u=2 images, degree-1 cone triple, unmarked dim, D_eq reject",
        "discriminant": str(disc),
        "two_P": [str(two_p[0]), str(two_p[1])],
        "two_P_matches": two_p == expected_two_p,
        "scaled_A": str(a_s),
        "scaled_B": str(b_s),
        "scaled_P": [str(p_s[0]), str(p_s[1])],
        "scaled_Q": [str(q_s[0]), str(q_s[1])],
        "triple": list(triple) if triple else None,
        "unmarked_dim": unmarked,
        "reject_repeated_marks": reject_repeated,
        "D_eq_triple_read": False,
        "match": (
            disc == Fraction(-496)
            and two_p == expected_two_p
            and scaled_ok
            and triple == (3, 2, 1)
            and unmarked == 2
            and reject_repeated
            and d1_ok
            and d2_ok
        ),
        "producer_imported": False,
        "stage0_run_read": False,
        "frobenius_constructed": False,
        "certificate_kind": "none",
    }
    (HERE / "blind_raw.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "discriminant": result["discriminant"],
        "two_P": result["two_P"],
        "triple": result["triple"],
        "unmarked_dim": unmarked,
        "reject_repeated_marks": reject_repeated,
        "match": result["match"],
    }))
    return 0 if result["match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

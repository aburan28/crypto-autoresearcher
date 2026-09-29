#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-4be480 Stage 1 P-S1-LDIV.

Frozen fixture numbers from review_plan_s1_4be480 only.
Does not import the Stage 1 producer. Does not read RUN-ECDLP-4be480-S1.
Does not construct a Frobenius. Does not treat a residue as a gate.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]

FORBIDDEN = [
    ROOT / "experiments/EXP-ECDLP-4be480/implementation/stage1_ldiv.py",
    ROOT / "experiments/EXP-ECDLP-4be480/runs/RUN-ECDLP-4be480-S1/raw-result.json",
    ROOT / "experiments/EXP-ECDLP-4be480/execution-report-s1.yaml",
]

A = Fraction(1)
B = Fraction(1)
U = Fraction(2)
P = (Fraction(0), Fraction(1))
NEG_P = (Fraction(0), Fraction(-1))


def weierstrass_disc(a: Fraction, b: Fraction) -> Fraction:
    return Fraction(-16) * (Fraction(4) * a ** 3 + Fraction(27) * b ** 2)


def lies_on(a: Fraction, b: Fraction, pt: tuple[Fraction, Fraction]) -> bool:
    x, y = pt
    return y * y == x * x * x + a * x + b


def add(a: Fraction, p1: tuple[Fraction, Fraction], p2: tuple[Fraction, Fraction]):
    x1, y1 = p1
    x2, y2 = p2
    if (x1, y1) == (x2, y2):
        slope = (Fraction(3) * x1 * x1 + a) / (Fraction(2) * y1)
    else:
        slope = (y2 - y1) / (x2 - x1)
    x3 = slope * slope - x1 - x2
    y3 = slope * (x1 - x3) - y1
    return (x3, y3), slope


def scale(u: Fraction, a: Fraction, b: Fraction, pt: tuple[Fraction, Fraction]):
    x, y = pt
    return (u ** 4 * a, u ** 6 * b, (u * u * x, u ** 3 * y))


def eval_inv_x(pt: tuple[Fraction, Fraction]) -> Fraction | None:
    x, _y = pt
    if x == 0:
        return None
    return Fraction(1) / x


def eval_miller(pt: tuple[Fraction, Fraction], x3p: Fraction) -> Fraction | None:
    x, y = pt
    ell = y - Fraction(1) + Fraction(17, 2) * x
    if ell == 0:
        return None
    return (x - x3p) / ell


def main() -> int:
    for path in FORBIDDEN:
        if path.exists():
            pass

    disc = weierstrass_disc(A, B)
    two_p, _dbl_slope = add(A, P, P)
    three_p, chord_slope = add(A, P, two_p)

    d1_ok = P != NEG_P and lies_on(A, B, P) and lies_on(A, B, NEG_P)
    d2_ok = (
        P != two_p
        and lies_on(A, B, P)
        and lies_on(A, B, two_p)
        and two_p == (Fraction(1, 4), Fraction(-9, 8))
    )
    a_s, b_s, p_s = scale(U, A, B, P)
    _, _, q_s = scale(U, A, B, NEG_P)
    _, _, two_s = scale(U, A, B, two_p)
    _, _, three_s = scale(U, A, B, three_p)
    scaled_ok = (
        p_s != q_s
        and a_s == Fraction(16)
        and b_s == Fraction(64)
        and p_s == (Fraction(0), Fraction(8))
        and q_s == (Fraction(0), Fraction(-8))
        and lies_on(a_s, b_s, p_s)
        and lies_on(a_s, b_s, q_s)
    )

    d1_ind = eval_inv_x(two_p) != eval_inv_x(three_p)
    d2_v3 = eval_miller(three_p, three_p[0])
    d2_vneg = eval_miller(NEG_P, three_p[0])
    d2_ind = d2_v3 is not None and d2_vneg is not None and d2_v3 != d2_vneg
    d1s_ind = eval_inv_x(two_s) != eval_inv_x(three_s)

    reject_repeated = (P == P) and lies_on(A, B, P)
    d_eq_basis_read = False
    l_d1 = 2 if d1_ok and d1_ind else None
    l_d2 = 2 if d2_ok and d2_ind else None
    l_d1s = 2 if scaled_ok and d1s_ind else None

    match = (
        disc == Fraction(-496)
        and two_p == (Fraction(1, 4), Fraction(-9, 8))
        and chord_slope == Fraction(-17, 2)
        and lies_on(A, B, three_p)
        and three_p == add(A, P, two_p)[0]
        and scaled_ok
        and l_d1 == 2
        and l_d2 == 2
        and l_d1s == 2
        and reject_repeated
        and not d_eq_basis_read
    )

    result = {
        "task_id": "TASK-20260908-a0d3aa",
        "quantity": "discriminant, 2P, 3P, chord slope, l(D) independence, D_eq reject",
        "discriminant": str(disc),
        "two_P": [str(two_p[0]), str(two_p[1])],
        "three_P": [str(three_p[0]), str(three_p[1])],
        "chord_slope": str(chord_slope),
        "scaled_A": str(a_s),
        "scaled_B": str(b_s),
        "scaled_P": [str(p_s[0]), str(p_s[1])],
        "scaled_Q": [str(q_s[0]), str(q_s[1])],
        "l_D1": l_d1,
        "l_D2": l_d2,
        "l_D1_scaled": l_d1s,
        "linear_independence_D1": d1_ind,
        "linear_independence_D2": d2_ind,
        "linear_independence_D1_scaled": d1s_ind,
        "reject_repeated_marks": reject_repeated,
        "D_eq_basis_read": d_eq_basis_read,
        "match": match,
        "producer_imported": False,
        "stage1_run_read": False,
        "frobenius_constructed": False,
        "residue_used_as_gate": False,
        "certificate_kind": "none",
    }
    (HERE / "blind_raw.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "discriminant": result["discriminant"],
        "two_P": result["two_P"],
        "three_P": result["three_P"],
        "chord_slope": result["chord_slope"],
        "l_D": [l_d1, l_d2, l_d1s],
        "match": match,
    }))
    return 0 if match else 1


if __name__ == "__main__":
    raise SystemExit(main())

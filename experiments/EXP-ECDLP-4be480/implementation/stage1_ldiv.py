#!/usr/bin/env python3
"""EXP-ECDLP-4be480 Stage 1 explicit L(D) bases.

Frozen object P-S1-LDIV. Certificate kind none.
No Frobenius. No Kedlaya. No Serre-Tate.
Residue / leading coefficient is an observation, not a gate.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN_DIR = ROOT / "experiments/EXP-ECDLP-4be480/runs/RUN-ECDLP-4be480-S1"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-4be480/execution-report-s1.yaml"
AUTHORIZED_BY = "DEC-20260908-477c65"
TASK_ID = "TASK-20260908-f19f8a"

A = Fraction(1)
B = Fraction(1)
U = Fraction(2)
SLOPE = Fraction(-17, 2)


def disc(a: Fraction, b: Fraction) -> Fraction:
    return Fraction(-16) * (Fraction(4) * a ** 3 + Fraction(27) * b ** 2)


def on_curve(a: Fraction, b: Fraction, x: Fraction, y: Fraction) -> bool:
    return y * y == x * x * x + a * x + b


def add(
    a: Fraction,
    P: tuple[Fraction, Fraction],
    Q: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    x1, y1 = P
    x2, y2 = Q
    if (x1, y1) == (x2, y2):
        lam = (Fraction(3) * x1 * x1 + a) / (Fraction(2) * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)


def double(a: Fraction, P: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return add(a, P, P)


def scale_point(u: Fraction, P: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    x, y = P
    return (u * u * x, u * u * u * y)


def scale_curve(u: Fraction, a: Fraction, b: Fraction) -> tuple[Fraction, Fraction]:
    return (u ** 4 * a, u ** 6 * b)


def pair_ok(a: Fraction, b: Fraction, P, Q) -> dict:
    px, py = P
    qx, qy = Q
    distinct = (px, py) != (qx, qy)
    on_p = on_curve(a, b, px, py)
    on_q = on_curve(a, b, qx, qy)
    return {
        "distinct": distinct,
        "on_curve_P": on_p,
        "on_curve_Q": on_q,
        "admissible": distinct and on_p and on_q,
    }


def dy_dx(a: Fraction, x: Fraction, y: Fraction) -> Fraction:
    return (Fraction(3) * x * x + a) / (Fraction(2) * y)


def residue_1_over_x(mark: tuple[Fraction, Fraction]) -> Fraction | None:
    """Residue of 1/x in the local parameter x at a mark with x=0, y!=0."""
    x, y = mark
    if x != 0 or y == 0:
        return None
    # 1/x has Laurent series 1/x; d(x)/dx = 1.
    return Fraction(1)


def residue_miller(
    a: Fraction,
    mark: tuple[Fraction, Fraction],
    x3p: Fraction,
    y_offset: Fraction,
    slope: Fraction,
) -> Fraction | None:
    """Residue of (x-x3P)/ell in local parameter x.

    Frozen chord is ell = y - 1 + (17/2)x.
    """
    x, y = mark
    if y == 0:
        return None
    num = x - x3p
    # ell = y - 1 + (17/2) x
    ell = y - y_offset + (Fraction(17, 2) * x)
    if ell != 0 or num == 0:
        return None
    dell_dx = Fraction(17, 2) + dy_dx(a, x, y)
    if dell_dx == 0:
        return None
    return num / dell_dx


def eval_1_over_x(P: tuple[Fraction, Fraction]) -> Fraction | None:
    x, _y = P
    if x == 0:
        return None
    return Fraction(1) / x


def eval_miller(
    P: tuple[Fraction, Fraction],
    x3p: Fraction,
    y_offset: Fraction,
) -> Fraction | None:
    x, y = P
    ell = y - y_offset + (Fraction(17, 2) * x)
    if ell == 0:
        return None
    return (x - x3p) / ell


def lin_ind_two_values(v1: Fraction | None, v2: Fraction | None) -> bool:
    """{1, f} are Q-linearly independent if f takes two distinct finite values."""
    if v1 is None or v2 is None:
        return False
    return v1 != v2


def main() -> int:
    t0 = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    d = disc(A, B)
    P1 = (Fraction(0), Fraction(1))
    Q1 = (Fraction(0), Fraction(-1))
    Q2 = double(A, P1)
    expected_q2 = (Fraction(1, 4), Fraction(-9, 8))
    P3 = add(A, P1, Q2)
    expected_p3 = (Fraction(72), Fraction(611))
    chord_slope = (Q2[1] - P1[1]) / (Q2[0] - P1[0])
    A_s, B_s = scale_curve(U, A, B)
    P1s = scale_point(U, P1)
    Q1s = scale_point(U, Q1)
    P2s = scale_point(U, Q2)
    P3s = scale_point(U, P3)

    d1 = pair_ok(A, B, P1, Q1)
    d2 = pair_ok(A, B, P1, Q2)
    d1s = pair_ok(A_s, B_s, P1s, Q1s)
    deq = pair_ok(A, B, P1, P1)
    reject_repeated = (not deq["distinct"]) and deq["on_curve_P"]

    # Do not read an L(D) basis on D_eq.
    # Nearby-object L(0): constants only, dim 1.
    l0 = 1

    # D1 and D1-scaled: basis {1, 1/x}. Witness independence by two values.
    d1_v_2p = eval_1_over_x(Q2)
    d1_v_3p = eval_1_over_x(P3)
    d1_ind = lin_ind_two_values(d1_v_2p, d1_v_3p)
    d1s_v_2p = eval_1_over_x(P2s)
    d1s_v_3p = eval_1_over_x(P3s)
    d1s_ind = lin_ind_two_values(d1s_v_2p, d1s_v_3p)

    # D2: basis {1, (x-x_3P)/ell}. f(3P)=0; f at a regular non-pole is nonzero.
    d2_v_3p = eval_miller(P3, P3[0], Fraction(1))
    # A regular test point: -P = (0, -1) is not a pole of the Miller function
    # (ell(-P) = -1 - 1 + 0 = -2 != 0).
    d2_v_negp = eval_miller(Q1, P3[0], Fraction(1))
    d2_ind = lin_ind_two_values(d2_v_3p, d2_v_negp)

    l_d1 = 2 if d1["admissible"] and d1_ind else None
    l_d2 = 2 if d2["admissible"] and d2_ind else None
    l_d1s = 2 if d1s["admissible"] and d1s_ind else None

    # Residues: observation only.
    res_d1_p = residue_1_over_x(P1)
    res_d1_q = residue_1_over_x(Q1)
    res_d2_p = residue_miller(A, P1, P3[0], Fraction(1), SLOPE)
    res_d2_q = residue_miller(A, Q2, P3[0], Fraction(1), SLOPE)
    res_d1s_p = residue_1_over_x(P1s)
    res_d1s_q = residue_1_over_x(Q1s)

    fixture_pass = (
        d == Fraction(-496)
        and d1["admissible"]
        and d2["admissible"]
        and d1s["admissible"]
        and Q2 == expected_q2
        and P3 == expected_p3
        and on_curve(A, B, P3[0], P3[1])
        and chord_slope == SLOPE
        and (P1s, Q1s) == ((Fraction(0), Fraction(8)), (Fraction(0), Fraction(-8)))
        and A_s == Fraction(16)
        and B_s == Fraction(64)
        and reject_repeated
    )
    ldiv_pass = (
        fixture_pass
        and l_d1 == 2
        and l_d2 == 2
        and l_d1s == 2
        and d1_ind
        and d2_ind
        and d1s_ind
        and l0 == 1
    )
    # Rank collision of the two-mark spaces: both have l(D)=2.
    # A residue difference is not this gate.
    mark_collision_pass = fixture_pass and l_d1 == 2 and l_d2 == 2
    all_pass = (
        fixture_pass
        and ldiv_pass
        and mark_collision_pass
        and reject_repeated
    )
    elapsed = time.time() - t0

    def fr(v: Fraction | None) -> str | None:
        return None if v is None else str(v)

    raw = {
        "run_id": "RUN-ECDLP-4be480-S1",
        "experiment_id": "EXP-ECDLP-4be480",
        "hypothesis_id": "H-ECDLP-2ac931",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 1,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S1-LDIV",
        "residue_observation_is_not_a_gate": True,
        "fixture": {
            "A": "1",
            "B": "1",
            "discriminant": str(d),
            "D1": {
                "P": ["0", "1"],
                "Q": ["0", "-1"],
                "L_basis": ["1", "1/x"],
                **{k: v for k, v in d1.items()},
            },
            "D2": {
                "P": ["0", "1"],
                "Q": [str(Q2[0]), str(Q2[1])],
                "equals_2P": Q2 == expected_q2,
                "computed_3P": [str(P3[0]), str(P3[1])],
                "equals_P_plus_2P": P3 == expected_p3,
                "chord_slope": str(chord_slope),
                "L_basis": ["1", "(x-x_3P)/(y-1+(17/2)*x)"],
                **{k: v for k, v in d2.items()},
            },
            "D1_scaled": {
                "u": "2",
                "A": str(A_s),
                "B": str(B_s),
                "P": [str(P1s[0]), str(P1s[1])],
                "Q": [str(Q1s[0]), str(Q1s[1])],
                "L_basis": ["1", "1/x"],
                **{k: v for k, v in d1s.items()},
            },
            "D_eq_rejected": reject_repeated,
            "unmarked_l0": l0,
            "frobenius_constructed": False,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "ldiv_pass": ldiv_pass,
            "mark_collision_pass": mark_collision_pass,
            "reject_repeated_marks": reject_repeated,
            "l_D1": l_d1,
            "l_D2": l_d2,
            "l_D1_scaled": l_d1s,
            "linear_independence_D1": d1_ind,
            "linear_independence_D2": d2_ind,
            "linear_independence_D1_scaled": d1s_ind,
            "computed_3P": [str(P3[0]), str(P3[1])],
            "residue_observation": {
                "is_not_a_gate": True,
                "D1": {"P": fr(res_d1_p), "Q": fr(res_d1_q), "local_param": "x"},
                "D2": {"P": fr(res_d2_p), "Q": fr(res_d2_q), "local_param": "x"},
                "D1_scaled": {"P": fr(res_d1s_p), "Q": fr(res_d1s_q), "local_param": "x"},
            },
            "independence_witnesses": {
                "D1": {"f_at_2P": fr(d1_v_2p), "f_at_3P": fr(d1_v_3p)},
                "D2": {"f_at_3P": fr(d2_v_3p), "f_at_negP": fr(d2_v_negp)},
                "D1_scaled": {"f_at_2P_scaled": fr(d1s_v_2p), "f_at_3P_scaled": fr(d1s_v_3p)},
            },
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage2_authorized": False,
        "exp_6a97f4_stage2_authorized": False,
        "exp_420e73_stage17_authorized": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_a_frobenius": True,
        "not_kedlaya": True,
        "not_a_canonicality_claim": True,
        "not_an_H1_claim": True,
        "not_P_S1_DIGIT": True,
        "not_P_S1_RELATIVE": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }

    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-4be480/implementation/stage1_ldiv.py\n"
    )
    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "executable": sys.executable,
    }
    (RUN_DIR / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    (RUN_DIR / "stdout.log").write_text(
        json.dumps(
            {
                "fixture_pass": fixture_pass,
                "ldiv_pass": ldiv_pass,
                "mark_collision_pass": mark_collision_pass,
                "reject_repeated_marks": reject_repeated,
                "l_D": {"D1": l_d1, "D2": l_d2, "D1_scaled": l_d1s},
                "computed_3P": [str(P3[0]), str(P3[1])],
                "residue_observation_is_not_a_gate": True,
            },
            indent=2,
        )
        + "\n"
    )
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-4be480-S1
  experiment_id: EXP-ECDLP-4be480
  run_id: RUN-ECDLP-4be480-S1
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 1
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  ldiv_pass: {str(ldiv_pass).lower()}
  mark_collision_pass: {str(mark_collision_pass).lower()}
  reject_repeated_marks: {str(reject_repeated).lower()}
  residue_observation_is_not_a_gate: true
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_a98ea9_stage5_authorized: false
  exp_420e73_stage17_authorized: false
  exp_6a97f4_stage2_authorized: false
  stage2_authorized: false
  not_an_H1_claim: true
  not_a_canonicality_claim: true
  not_a_frobenius: true
  not_kedlaya: true
  frozen_object: P-S1-LDIV
  observations:
  - fixture_pass {str(fixture_pass).lower()}. discriminant {d}. D2 Q equals 2*(0,1). 3P equals P+2P. u=2 images reused.
  - ldiv_pass {str(ldiv_pass).lower()}. l(D)=2 on D1, D2, and D1-scaled with frozen bases linearly independent over Q.
  - mark_collision_pass {str(mark_collision_pass).lower()} as l(D1)=l(D2)=2. Residue difference is not this gate.
  - D_eq repeated marks rejected before any L(D) basis was read.
  unexpected_observations: []
  scientific_boundary: Toy one-curve explicit L(D) bases over Q. Not a Frobenius. Not Kedlaya. Not Serre-Tate. Not P-S1-DIGIT. Not P-S1-RELATIVE. Not H1. Not a W class. Stage 2 of EXP-ECDLP-4be480 is not authorized. Stage 2 of EXP-ECDLP-6a97f4 is not authorized. Stage 17 of EXP-ECDLP-420e73 is not authorized. No a98ea9 Stage 5. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    print(
        json.dumps(
            {
                "all_pass": all_pass,
                "elapsed": elapsed,
                "l_D": [l_d1, l_d2, l_d1s],
                "computed_3P": [str(P3[0]), str(P3[1])],
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

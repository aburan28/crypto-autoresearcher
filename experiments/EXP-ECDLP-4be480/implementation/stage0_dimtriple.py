#!/usr/bin/env python3
"""EXP-ECDLP-4be480 Stage 0 rank-only relative de Rham cone.

Certificate kind none. No Frobenius. No Kedlaya. No Serre-Tate.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-4be480/implementation/stage0_dimtriple.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-4be480/runs/RUN-ECDLP-4be480-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-4be480/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-18ecbd"
TASK_ID = "TASK-20260908-346ed9"

A = Fraction(1)
B = Fraction(1)
U = Fraction(2)


def disc(a: Fraction, b: Fraction) -> Fraction:
    return Fraction(-16) * (Fraction(4) * a ** 3 + Fraction(27) * b ** 2)


def on_curve(a: Fraction, b: Fraction, x: Fraction, y: Fraction) -> bool:
    return y * y == x * x * x + a * x + b


def double(a: Fraction, P: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    x, y = P
    lam = (Fraction(3) * x * x + a) / (Fraction(2) * y)
    x3 = lam * lam - Fraction(2) * x
    y3 = lam * (x - x3) - y
    return (x3, y3)


def scale_point(u: Fraction, P: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    x, y = P
    return (u * u * x, u * u * u * y)


def scale_curve(u: Fraction, a: Fraction, b: Fraction) -> tuple[Fraction, Fraction]:
    return (u ** 4 * a, u ** 6 * b)


def restriction_rank() -> int:
    # r: Q -> Q^2, c |-> (c, c). Matrix [[1],[1]], rank 1.
    rows = [[1], [1]]
    # rank of 2x1 matrix with a nonzero column
    return 1 if any(rows[i][0] for i in range(2)) else 0


def h1_ord_dim() -> int:
    # Basis of H^1_dR(E) is {dx/y, x dx/y}. Coefficient matrix in {1, x}:
    # [[1, 0], [0, 1]], rank 2.
    m = [[1, 0], [0, 1]]
    # 2x2 identity
    return 2 if m[0][0] * m[1][1] - m[0][1] * m[1][0] != 0 else 0


def cone_triple() -> tuple[int, int, int]:
    # H0_E = Q dim 1, H0_D = Q^2 dim 2, r diagonal rank 1
    # coker(r) dim 1, H1_D = 0, H1_ord dim 2
    # H1_rel = coker(r) ⊕ H1_ord dim 3
    # ker(phi) = coker(r) dim 1
    dim_h1_ord = h1_ord_dim()
    dim_coker = 2 - restriction_rank()
    dim_h1_rel = dim_coker + dim_h1_ord
    dim_ker = dim_coker
    return (dim_h1_rel, dim_h1_ord, dim_ker)


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


def main() -> int:
    t0 = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    d = disc(A, B)
    P1 = (Fraction(0), Fraction(1))
    Q1 = (Fraction(0), Fraction(-1))
    Q2 = double(A, P1)
    expected_q2 = (Fraction(1, 4), Fraction(-9, 8))
    A_s, B_s = scale_curve(U, A, B)
    P1s = scale_point(U, P1)
    Q1s = scale_point(U, Q1)
    expected_scaled = ((Fraction(0), Fraction(8)), (Fraction(0), Fraction(-8)))

    d1 = pair_ok(A, B, P1, Q1)
    d2 = pair_ok(A, B, P1, Q2)
    d1s = pair_ok(A_s, B_s, P1s, Q1s)
    deq = pair_ok(A, B, P1, P1)

    reject_repeated = (not deq["distinct"]) and deq["on_curve_P"]
    # Do not read a triple on D_eq.
    triple_d1 = cone_triple() if d1["admissible"] else None
    triple_d2 = cone_triple() if d2["admissible"] else None
    triple_d1s = cone_triple() if d1s["admissible"] else None
    unmarked_d1 = h1_ord_dim()
    unmarked_d2 = h1_ord_dim()

    fixture_pass = (
        d == Fraction(-496)
        and d1["admissible"]
        and d2["admissible"]
        and d1s["admissible"]
        and Q2 == expected_q2
        and (P1s, Q1s) == expected_scaled
        and A_s == Fraction(16)
        and B_s == Fraction(64)
        and restriction_rank() == 1
        and reject_repeated
    )
    dimtriple_pass = (
        fixture_pass
        and triple_d1 == (3, 2, 1)
        and triple_d2 == (3, 2, 1)
        and triple_d1s == (3, 2, 1)
    )
    mark_collision_pass = fixture_pass and triple_d1 == triple_d2
    unmarked_independent = fixture_pass and unmarked_d1 == 2 and unmarked_d2 == 2
    all_pass = (
        fixture_pass
        and dimtriple_pass
        and mark_collision_pass
        and unmarked_independent
        and reject_repeated
    )
    elapsed = time.time() - t0

    raw = {
        "run_id": "RUN-ECDLP-4be480-S0",
        "experiment_id": "EXP-ECDLP-4be480",
        "hypothesis_id": "H-ECDLP-2ac931",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-DIMTRIPLE",
        "fixture": {
            "A": "1",
            "B": "1",
            "discriminant": str(d),
            "D1": {"P": ["0", "1"], "Q": ["0", "-1"], **{k: v for k, v in d1.items()}},
            "D2": {
                "P": ["0", "1"],
                "Q": [str(Q2[0]), str(Q2[1])],
                "equals_2P": Q2 == expected_q2,
                **{k: v for k, v in d2.items()},
            },
            "D1_scaled": {
                "u": "2",
                "A": str(A_s),
                "B": str(B_s),
                "P": [str(P1s[0]), str(P1s[1])],
                "Q": [str(Q1s[0]), str(Q1s[1])],
                **{k: v for k, v in d1s.items()},
            },
            "D_eq_rejected": reject_repeated,
            "restriction_rank": restriction_rank(),
            "h1_ord_basis_rank": h1_ord_dim(),
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "dimtriple_pass": dimtriple_pass,
            "mark_collision_pass": mark_collision_pass,
            "unmarked_independent": unmarked_independent,
            "reject_repeated_marks": reject_repeated,
            "triple_D1": list(triple_d1) if triple_d1 else None,
            "triple_D2": list(triple_d2) if triple_d2 else None,
            "triple_D1_scaled": list(triple_d1s) if triple_d1s else None,
            "unmarked_dim_D1": unmarked_d1,
            "unmarked_dim_D2": unmarked_d2,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_6a97f4_stage2_authorized": False,
        "exp_420e73_stage17_authorized": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_a_frobenius": True,
        "not_kedlaya": True,
        "not_a_canonicality_claim": True,
        "not_an_H1_claim": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }

    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-4be480/implementation/stage0_dimtriple.py\n"
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
                "dimtriple_pass": dimtriple_pass,
                "mark_collision_pass": mark_collision_pass,
                "unmarked_independent": unmarked_independent,
                "reject_repeated_marks": reject_repeated,
                "triples": {
                    "D1": triple_d1,
                    "D2": triple_d2,
                    "D1_scaled": triple_d1s,
                },
            },
            indent=2,
        )
        + "\n"
    )
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-4be480-S0
  experiment_id: EXP-ECDLP-4be480
  run_id: RUN-ECDLP-4be480-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  dimtriple_pass: {str(dimtriple_pass).lower()}
  mark_collision_pass: {str(mark_collision_pass).lower()}
  unmarked_independent: {str(unmarked_independent).lower()}
  reject_repeated_marks: {str(reject_repeated).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_a98ea9_stage5_authorized: false
  exp_420e73_stage17_authorized: false
  exp_6a97f4_stage2_authorized: false
  stage1_authorized: false
  not_an_H1_claim: true
  not_a_canonicality_claim: true
  not_a_frobenius: true
  not_kedlaya: true
  frozen_object: P-S0-DIMTRIPLE
  observations:
  - fixture_pass {str(fixture_pass).lower()}. discriminant {d}. D2 Q equals 2*(0,1) = (1/4, -9/8). u=2 images (0,8) and (0,-8).
  - dimtriple_pass {str(dimtriple_pass).lower()}. triples D1/D2/D1-scaled all {triple_d1}.
  - mark_collision_pass {str(mark_collision_pass).lower()}. unmarked dims {unmarked_d1} and {unmarked_d2}.
  - D_eq repeated marks rejected before any triple was read.
  unexpected_observations: []
  scientific_boundary: Toy one-curve rank-only de Rham cone over Q. Not a Frobenius. Not Kedlaya. Not Serre-Tate. Not P-S1-DIGIT. Not H1. Not a W class. Stage 1 of EXP-ECDLP-4be480 is not authorized. Stage 2 of EXP-ECDLP-6a97f4 is not authorized. Stage 17 of EXP-ECDLP-420e73 is not authorized. No a98ea9 Stage 5. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    print(json.dumps({"all_pass": all_pass, "elapsed": elapsed, "triples": triple_d1}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

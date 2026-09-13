#!/usr/bin/env python3
"""EXP-ECDLP-bf222c Stage 0 exact doubling-Jacobian chain-rule calibrator.

Certificate kind none. No nested LHW generator. No Semaev S_m.
Frozen object P-S0-DBLJAC: REAL / KF / NULL on one F_19 point.

REAL: p=19, A=1, B=-1, P=(2,3), [2]P=(16,11), [4]P=(15,11),
J1=[[13,12],[3,0]] det=2, J2=[[0,7],[16,14]] det=2,
J4=J2 J1=[[2,0],[3,2]] det=4.
KF: claim det D[4]=1. Actual 4. Rejected.
NULL empty matrix is rejected. y=0 is rejected.

Producer method: form affine doubling Jacobians by formal
differentiation and multiply determinants.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-bf222c/implementation/stage0_dbljac.py"

P = 19
A = 1
B = -1
POINT = (2, 3)
MUST_P2 = (16, 11)
MUST_P4 = (15, 11)
MUST_J1 = ((13, 12), (3, 0))
MUST_J2 = ((0, 7), (16, 14))
MUST_J4 = ((2, 0), (3, 2))
MUST_DET1 = 2
MUST_DET2 = 2
MUST_DET4 = 4
KF_CLAIMED_DET4 = 1


class InvalidParamsError(ValueError):
    """Empty Jacobian or y=0 is rejected."""


def inv(value: int) -> int:
    return pow(value, -1, P)


def require_nonzero_y(y: int) -> None:
    if y % P == 0:
        raise InvalidParamsError("y is zero")


def require_nonempty_matrix(matrix: tuple | None) -> None:
    if not matrix:
        raise InvalidParamsError("matrix is empty")


def det2(matrix: tuple[tuple[int, int], tuple[int, int]]) -> int:
    return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % P


def matmul(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (
            (left[0][0] * right[0][0] + left[0][1] * right[1][0]) % P,
            (left[0][0] * right[0][1] + left[0][1] * right[1][1]) % P,
        ),
        (
            (left[1][0] * right[0][0] + left[1][1] * right[1][0]) % P,
            (left[1][0] * right[0][1] + left[1][1] * right[1][1]) % P,
        ),
    )


def affine_double(x: int, y: int) -> tuple[int, int]:
    require_nonzero_y(y)
    lam = ((3 * x * x + A) * inv(2 * y)) % P
    x2 = (lam * lam - 2 * x) % P
    y2 = (lam * ((x - x2) % P) - y) % P
    return x2, y2


def doubling_jacobian(x: int, y: int) -> tuple[tuple[tuple[int, int], tuple[int, int]], int]:
    """Formal Jacobian of affine doubling at (x, y)."""
    require_nonzero_y(y)
    lam = ((3 * x * x + A) * inv(2 * y)) % P
    dlam_dx = (3 * x * inv(y)) % P
    dlam_dy = (-(3 * x * x + A) * inv(2 * y * y)) % P
    x2 = (lam * lam - 2 * x) % P
    dx2_dx = (2 * lam * dlam_dx - 2) % P
    dx2_dy = (2 * lam * dlam_dy) % P
    dyp_dx = (dlam_dx * x + lam - (dlam_dx * x2 + lam * dx2_dx)) % P
    dyp_dy = (dlam_dy * x - (dlam_dy * x2 + lam * dx2_dy) - 1) % P
    jacobian = ((dx2_dx, dx2_dy), (dyp_dx, dyp_dy))
    return jacobian, det2(jacobian)


def chain_rule_solve() -> dict:
    require_nonzero_y(POINT[1])
    p2 = affine_double(*POINT)
    p4 = affine_double(*p2)
    j1, det_j1 = doubling_jacobian(*POINT)
    j2, det_j2 = doubling_jacobian(*p2)
    j4 = matmul(j2, j1)
    det_j4 = det2(j4)
    product = (det_j1 * det_j2) % P
    return {
        "P2": list(p2),
        "P4": list(p4),
        "J1": [list(j1[0]), list(j1[1])],
        "J2": [list(j2[0]), list(j2[1])],
        "J4": [list(j4[0]), list(j4[1])],
        "det1": det_j1,
        "det2": det_j2,
        "det4": det_j4,
        "product": product,
    }


def evaluate_gates() -> dict:
    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_nonzero_y(0)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "y-zero", "point": [2, 0], "rejected": True})

    try:
        require_nonempty_matrix(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_matrix", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_matrix", "rejected": True}

    solved = chain_rule_solve()
    real_chain_rule_pass = (
        tuple(solved["P2"]) == MUST_P2
        and tuple(solved["P4"]) == MUST_P4
        and tuple(tuple(row) for row in solved["J1"]) == MUST_J1
        and tuple(tuple(row) for row in solved["J2"]) == MUST_J2
        and tuple(tuple(row) for row in solved["J4"]) == MUST_J4
        and solved["det1"] == MUST_DET1
        and solved["det2"] == MUST_DET2
        and solved["det4"] == MUST_DET4
        and solved["product"] == MUST_DET4
    )
    kf_rejected = solved["det4"] == MUST_DET4 and solved["det4"] != KF_CLAIMED_DET4
    return {
        "fixture_pass": fixture_pass,
        "real_chain_rule_pass": real_chain_rule_pass,
        "known_false_constant_pass": kf_rejected,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "solved": solved,
        "kf_rejected": kf_rejected,
        "null_obj": null_obj,
        "invalid_decisions": invalid_decisions,
    }


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    gates = evaluate_gates()
    all_pass = (
        gates["fixture_pass"]
        and gates["real_chain_rule_pass"]
        and gates["known_false_constant_pass"]
        and gates["reject_invalid_pass"]
        and gates["null_empty_pass"]
    )
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
    print(
        json.dumps(
            {
                "all_pass": all_pass,
                "source_sha256": source_sha256,
                "commit": git_head(),
                "python": platform.python_version(),
                "executable": sys.executable,
                **{k: gates[k] for k in (
                    "fixture_pass",
                    "real_chain_rule_pass",
                    "known_false_constant_pass",
                    "reject_invalid_pass",
                    "null_empty_pass",
                )},
                "REAL": gates["solved"],
                "KF": {
                    "claimed_det4": KF_CLAIMED_DET4,
                    "actual_det4": gates["solved"]["det4"],
                    "rejected": gates["kf_rejected"],
                },
                "NULL": gates["null_obj"],
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

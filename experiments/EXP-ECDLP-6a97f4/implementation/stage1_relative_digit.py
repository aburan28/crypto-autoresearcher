#!/usr/bin/env python3
"""EXP-ECDLP-6a97f4 Stage 1 P-S1-RELATIVE digit audit.

Certificate kind none. Canonicality uncertified. P-S1-DIGIT untested.
relative_sensitivity_pass is an observation, not a gate.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-6a97f4/implementation/stage1_relative_digit.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-6a97f4/runs/RUN-ECDLP-6a97f4-S1"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-6a97f4/execution-report-s1.yaml"
AUTHORIZED_BY = "DEC-20260908-384100"
TASK_ID = "TASK-20260908-acbd1a"

CELLS = [
    {"id": "S0-C13", "p": 13, "A": 1, "B": 5, "n": 9, "P": (3, 3)},
    {"id": "S0-C17", "p": 17, "A": 1, "B": 5, "n": 15, "P": (2, 7)},
    {"id": "S0-C19", "p": 19, "A": 1, "B": 1, "n": 21, "P": (0, 1)},
    {"id": "S0-C37", "p": 37, "A": 1, "B": 3, "n": 39, "P": (0, 15)},
]
SCALINGS = [2, 3]
PERTURBATIONS = [
    {"id": "P10", "a": 1, "b": 0},
    {"id": "P01", "a": 0, "b": 1},
    {"id": "P11", "a": 1, "b": 1},
]


def add(mod: int, a: int, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % mod == 0:
        return None
    if P == Q:
        if y1 % mod == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, mod) % mod
    else:
        lam = (y2 - y1) * pow((x2 - x1) % mod, -1, mod) % mod
    x3 = (lam * lam - x1 - x2) % mod
    y3 = (lam * (x1 - x3) - y1) % mod
    return (x3, y3)


def scal(mod: int, a: int, k: int, P):
    R = None
    Q = P
    while k:
        if k & 1:
            R = add(mod, a, R, Q)
        Q = add(mod, a, Q, Q)
        k >>= 1
    return R


def hensel_lift_point(p: int, A: int, B: int, P):
    """Lift a nonsingular affine point from F_p to Z/p^2 by Hensel on y at fixed x."""
    x0, y0 = P
    mod = p * p
    fx = (pow(x0, 3, mod) + A * x0 + B) % mod
    rhs = (fx - (y0 * y0) % mod) % mod
    assert rhs % p == 0, (P, rhs)
    if (2 * y0) % p == 0:
        raise RuntimeError(f"y=0 cannot lift uniquely: {P}")
    dy = ((rhs // p) * pow(2 * y0, -1, p)) % p
    y1 = (y0 + p * dy) % mod
    return (x0 % p, y1)


def F_of(x: int, A: int, mod: int) -> int:
    return (x * x) % mod * pow(A, -1, mod) % mod


def digit(F: int, p: int) -> int:
    """d(F)=((F-(F mod p))/p) mod p with 0..p-1 representatives of F in Z/p^2."""
    mod = p * p
    F = F % mod
    return ((F - (F % p)) // p) % p


def scaling_invariance_on_F(x: int, A: int, p: int) -> bool:
    mod = p * p
    F0 = F_of(x, A, mod)
    for u in SCALINGS:
        if pow(u, 1, p) == 0:
            raise RuntimeError(f"u={u} not a unit mod {p}")
        Ap = pow(u, 4, mod) * A % mod
        xp = pow(u, 2, mod) * x % mod
        if F_of(xp, Ap, mod) != F0:
            return False
    return True


def arm_model(cell: dict, a: int, b: int):
    p = cell["p"]
    return cell["A"] + a * p, cell["B"] + b * p


def sections_on_arm(cell: dict, A_lift: int, B_lift: int):
    p = cell["p"]
    A = cell["A"]
    n = cell["n"]
    P = cell["P"]
    mod = p * p
    rows = []
    for k in range(1, n):
        R = scal(p, A, k, P)
        if R is None:
            raise RuntimeError(f"{cell['id']}: [k]P hit O at k={k}")
        if R[1] % p == 0:
            raise RuntimeError(f"{cell['id']}: y=0 at k={k}")
        x1, y1 = hensel_lift_point(p, A_lift, B_lift, R)
        F = F_of(x1, A_lift, mod)
        rows.append(
            {
                "k": k,
                "x": x1,
                "F": F,
                "dF": digit(F, p),
                "scaling_ok": scaling_invariance_on_F(x1, A_lift, p),
            }
        )
    return rows


def run_cell(cell: dict) -> dict:
    p = cell["p"]
    n = cell["n"]
    A_base, B_base = arm_model(cell, 0, 0)
    base_rows = sections_on_arm(cell, A_base, B_base)
    n_sections = len(base_rows)
    expected = n - 1
    base_digits = [row["dF"] for row in base_rows]
    base_vs_base = sum(int(d1 != d2) for d1, d2 in zip(base_digits, base_digits))
    arms = {
        "BASE": {
            "A_lift": A_base,
            "B_lift": B_base,
            "canonicality_status": "uncertified",
            "n_sections": n_sections,
            "scaling_invariance_pass": all(row["scaling_ok"] for row in base_rows),
            "digits": base_digits,
        }
    }
    perturbations = []
    for pert in PERTURBATIONS:
        A_p, B_p = arm_model(cell, pert["a"], pert["b"])
        rows = sections_on_arm(cell, A_p, B_p)
        digits = [row["dF"] for row in rows]
        if len(digits) != n_sections:
            raise RuntimeError(f"{cell['id']} {pert['id']}: section count mismatch")
        n_digit_diff = sum(int(d0 != d1) for d0, d1 in zip(base_digits, digits))
        scaling_ok = all(row["scaling_ok"] for row in rows)
        arms[pert["id"]] = {
            "A_lift": A_p,
            "B_lift": B_p,
            "canonicality_status": "uncertified",
            "n_sections": len(rows),
            "scaling_invariance_pass": scaling_ok,
            "digits": digits,
        }
        perturbations.append(
            {
                "id": pert["id"],
                "n_digit_diff": n_digit_diff,
                "scaling_invariance_pass": scaling_ok,
                "canonicality_status": "uncertified",
            }
        )
    return {
        "id": cell["id"],
        "p": p,
        "n": n,
        "n_sections": n_sections,
        "expected_sections": expected,
        "base_vs_base_n_digit_diff": base_vs_base,
        "canonicality_status": "uncertified",
        "arms": arms,
        "perturbations": perturbations,
    }


def main() -> int:
    t0 = time.time()
    cells = [run_cell(c) for c in CELLS]
    n_digit_diff_panel = sum(
        pert["n_digit_diff"] for cell in cells for pert in cell["perturbations"]
    )
    sections_ok = all(c["n_sections"] == c["expected_sections"] for c in cells)
    base_vs_base_ok = all(c["base_vs_base_n_digit_diff"] == 0 for c in cells)
    scaling_ok = all(
        cell["arms"][arm]["scaling_invariance_pass"]
        for cell in cells
        for arm in ("BASE", "P10", "P01", "P11")
    )
    uncertified_ok = all(
        cell["arms"][arm]["canonicality_status"] == "uncertified"
        for cell in cells
        for arm in ("BASE", "P10", "P01", "P11")
    )
    fixture_pass = (
        sections_ok
        and base_vs_base_ok
        and scaling_ok
        and uncertified_ok
    )
    relative_sensitivity_pass = n_digit_diff_panel > 0
    result = {
        "run_id": "RUN-ECDLP-6a97f4-S1",
        "experiment_id": "EXP-ECDLP-6a97f4",
        "hypothesis_id": "H-ECDLP-e9d9bb",
        "authorized_by": AUTHORIZED_BY,
        "task_id": TASK_ID,
        "certificate": {"kind": "none"},
        "frozen_object": "P-S1-RELATIVE",
        "P_S1_DIGIT_untested": True,
        "not_a_canonicality_claim": True,
        "canonicality_status": "uncertified",
        "relative_sensitivity_pass_is_not_a_gate": True,
        "fixture_pass": fixture_pass,
        "relative_sensitivity_pass": relative_sensitivity_pass,
        "n_digit_diff_panel": n_digit_diff_panel,
        "base_vs_base_n_digit_diff_all_zero": base_vs_base_ok,
        "sections_ok": sections_ok,
        "scaling_invariance_pass": scaling_ok,
        "cells": [
            {
                "id": c["id"],
                "p": c["p"],
                "n": c["n"],
                "n_sections": c["n_sections"],
                "expected_sections": c["expected_sections"],
                "base_vs_base_n_digit_diff": c["base_vs_base_n_digit_diff"],
                "canonicality_status": c["canonicality_status"],
                "perturbations": c["perturbations"],
                "arms": {
                    arm: {
                        "canonicality_status": c["arms"][arm]["canonicality_status"],
                        "n_sections": c["arms"][arm]["n_sections"],
                        "scaling_invariance_pass": c["arms"][arm]["scaling_invariance_pass"],
                        "digits": c["arms"][arm]["digits"],
                    }
                    for arm in ("BASE", "P10", "P01", "P11")
                },
            }
            for c in cells
        ],
        "scalings": SCALINGS,
        "precision_r": 2,
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage2_authorized": False,
        "exp_420e73_stage17_authorized": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_an_H1_claim": True,
        "wall_clock_seconds": time.time() - t0,
        "python": sys.version,
        "platform": platform.platform(),
        "source": SOURCE,
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "raw-result.json").write_text(json.dumps(result, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(f"python3 {SOURCE}\n")
    env = {
        "python": "3.12.3",
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    (RUN_DIR / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    summary = json.dumps(
        {
            "fixture_pass": fixture_pass,
            "relative_sensitivity_pass": relative_sensitivity_pass,
            "n_digit_diff_panel": n_digit_diff_panel,
            "base_vs_base_n_digit_diff_all_zero": base_vs_base_ok,
            "sections_ok": sections_ok,
            "scaling_invariance_pass": scaling_ok,
            "certificate": {"kind": "none"},
            "canonicality_status": "uncertified",
            "P_S1_DIGIT_untested": True,
            "per_cell": [
                {
                    "id": c["id"],
                    "n_sections": c["n_sections"],
                    "base_vs_base_n_digit_diff": c["base_vs_base_n_digit_diff"],
                    "n_digit_diff": {
                        pert["id"]: pert["n_digit_diff"] for pert in c["perturbations"]
                    },
                }
                for c in cells
            ],
        },
        indent=2,
    ) + "\n"
    (RUN_DIR / "stdout.log").write_text(summary)
    (RUN_DIR / "stderr.log").write_text("")
    print(summary, end="")
    if not fixture_pass:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

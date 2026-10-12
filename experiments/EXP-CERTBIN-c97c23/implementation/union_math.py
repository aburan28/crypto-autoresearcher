#!/usr/bin/env python3
"""Pure arithmetic helpers for EXP-CERTBIN-c97c23 (no curve, no solver)."""
from __future__ import annotations

import math
from typing import Any


ARCHIVED_CEILINGS = [
    {
        "id": "audit-m83-a",
        "one_target": 2.5453522044710297e-18,
        "four_target": 1.0181408817884119e-17,
    },
    {
        "id": "audit-m83-b",
        "one_target": 8.564834857521739e-18,
        "four_target": 3.4259339430086955e-17,
    },
]

N = 19
M = 3
R = 130873
GROUP_ORDER_FULL = 4 * R
K = M // 2  # floor(m/2) = 1
L4 = 4
L32 = 32
BATCHES_L4 = 100
BATCHES_L32 = 20
MAX_IMAGE = 10_000_000
SEED_STAGE0 = 2026100414
SEED_STAGE1 = 2026100415
P_TARGETS = (
    {"id": "p_sparse", "target_p": 0.02},
    {"id": "p_half", "target_p": 0.5},
)


def binom(n: int, k: int) -> int:
    if k < 0 or n < 0 or k > n:
        return 0
    return math.comb(n, k)


def multiset_count(B: int, m: int) -> int:
    """C(B + m - 1, m) unordered m-multisets with repetition."""
    return binom(B + m - 1, m)


def complementary_half_fold_size(B: int, m: int = M) -> int:
    """T_test for m=3: enumerate C(B+1, 2) complementary pairs."""
    k = m // 2
    # complementary size is m - k
    return binom(B + (m - k) - 1, m - k)


def union_prob(p: float, L: int) -> float:
    """Numerically stable 1-(1-p)^L (float64 underflows at p ~ 1e-18)."""
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    # 1 - exp(L * log(1-p)) via expm1/log1p
    return -math.expm1(L * math.log1p(-p))


def rho_iteration_estimate(r: int = R, n: int = N, L: int = L4) -> float:
    return math.sqrt(math.pi * r / (4.0 * n)) * math.sqrt(L)


def choose_B_for_p(target_p: float, r: int = R, m: int = M) -> dict[str, Any]:
    """Smallest B with C(B+m-1,m)/r >= target_p * 0.8 and closest to target."""
    target_C = target_p * r
    best_B = 1
    best_err = float("inf")
    best_C = 0
    B = 1
    while True:
        C = multiset_count(B, m)
        if C > MAX_IMAGE:
            break
        err = abs(C - target_C)
        if err < best_err:
            best_err = err
            best_B = B
            best_C = C
        # stop searching once C is well above target and error is growing
        if C > target_C * 1.5 and err > best_err:
            break
        B += 1
        if B > 5000:
            break
    return {
        "B": best_B,
        "C": best_C,
        "C_over_r": best_C / r,
        "target_p": target_p,
        "enumerable": best_C <= MAX_IMAGE,
    }


def check_archived_identity(rel_tol: float = 1e-12) -> dict[str, Any]:
    rows = []
    ok = True
    for row in ARCHIVED_CEILINGS:
        p = row["one_target"]
        four_lin = 4.0 * p
        four_exact = union_prob(p, 4)
        lin_match = math.isclose(four_lin, row["four_target"], rel_tol=rel_tol, abs_tol=0.0)
        # rare-event: exact union ≈ linear form at these tiny p
        rare_match = math.isclose(four_exact, four_lin, rel_tol=1e-9, abs_tol=0.0)
        printed_match = math.isclose(four_exact, row["four_target"], rel_tol=1e-9, abs_tol=0.0)
        row_ok = lin_match and rare_match and printed_match
        ok = ok and row_ok
        rows.append(
            {
                "id": row["id"],
                "one_target": p,
                "four_target_printed": row["four_target"],
                "four_times_one": four_lin,
                "one_minus_one_minus_p_to_4": four_exact,
                "linear_matches_printed": lin_match,
                "rare_event_form_ok": rare_match,
                "exact_matches_printed": printed_match,
                "ok": row_ok,
            }
        )
    # nearby-object identity: at p=1/2, L=4, linearization error >= 1
    p_half = 0.5
    lin_err = (L4 * p_half) - union_prob(p_half, L4)
    rows.append(
        {
            "id": "nearby-p-half-identity",
            "p": p_half,
            "L": L4,
            "L_times_p": L4 * p_half,
            "one_minus_one_minus_p_to_L": union_prob(p_half, L4),
            "linearization_error": lin_err,
            "ok": lin_err >= 1.0 - 1e-12,
        }
    )
    ok = ok and lin_err >= 1.0 - 1e-12
    return {"archived_identity_ok": ok, "rows": rows}


def freeze_stage0() -> dict[str, Any]:
    identity = check_archived_identity()
    cells = []
    for spec in P_TARGETS:
        cell = choose_B_for_p(spec["target_p"])
        cell["id"] = spec["id"]
        cell["T_test_charged"] = complementary_half_fold_size(cell["B"])
        cell["rho_L4"] = rho_iteration_estimate(L=L4)
        cell["expected_tests_lower_L4"] = L4 / max(cell["C_over_r"], 1e-300)
        cell["expected_charged_lower_L4"] = cell["expected_tests_lower_L4"] * cell["T_test_charged"]
        cell["predicted_charged_ratio_L4"] = (
            cell["expected_charged_lower_L4"] / cell["rho_L4"]
        )
        cells.append(cell)
    return {
        "experiment_id": "EXP-CERTBIN-c97c23",
        "hypothesis_id": "H-CERTBIN-a916e0",
        "approved_by": "DEC-20261004-2be060",
        "n": N,
        "m": M,
        "k": K,
        "r": R,
        "group_order_full": GROUP_ORDER_FULL,
        "L_values": [L4, L32],
        "batches_L4": BATCHES_L4,
        "batches_L32": BATCHES_L32,
        "max_image_enumerations": MAX_IMAGE,
        "seed_stage0": SEED_STAGE0,
        "seed_stage1": SEED_STAGE1,
        "rho_formula": "sqrt(pi * r / (4 * n)) * sqrt(L)",
        "t_test_formula": "C(B+(m-k)-1, m-k) with k=floor(m/2)",
        "archived_identity": identity,
        "cells": cells,
        "preregistered_prediction": "O-RARE",
    }

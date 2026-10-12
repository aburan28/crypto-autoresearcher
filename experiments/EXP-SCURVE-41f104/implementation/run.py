#!/usr/bin/env python3
"""Stage-0 automorphism-cost certificate for EXP-SCURVE-41f104.

The five-percent band is the idea's reading. No 221-bit rho is run.
"""

from __future__ import annotations

import argparse
import json
from math import gcd
from pathlib import Path

EXPERIMENT_ID = "EXP-SCURVE-41f104"
RUN_ID = "RUN-SCURVE-5bc4fd"
CURVE_A = 117050
NEGATIVE_A = 0
TOY_ORDER = 10007


def j_invariant(coefficient_a: int) -> tuple[int, int] | None:
    denominator = coefficient_a * coefficient_a - 4
    if denominator == 0:
        return None
    numerator = 256 * (coefficient_a * coefficient_a - 3) ** 3
    common = gcd(numerator, denominator)
    return numerator // common, denominator // common


def automorphism_order(invariant: tuple[int, int] | None) -> int | None:
    if invariant is None:
        return None
    numerator, denominator = invariant
    if numerator == 0:
        return 6
    if numerator == 1728 * denominator:
        return 4
    return 2


def within_five_percent(aut_base: int, aut_adjusted: int) -> bool:
    return 361 * aut_adjusted <= 400 * aut_base <= 441 * aut_adjusted


def reading(coefficient_a: int, aut_base: int) -> dict:
    invariant = j_invariant(coefficient_a)
    order = automorphism_order(invariant)
    return {
        "A": coefficient_a,
        "aut_order": order,
        "defined": invariant is not None,
        "j_denominator": None if invariant is None else invariant[1],
        "j_numerator": None if invariant is None else invariant[0],
        "within_five_percent": order is not None and within_five_percent(aut_base, order),
    }


def census() -> dict:
    main = reading(CURVE_A, 2)
    negative = reading(NEGATIVE_A, 2)
    null_within = within_five_percent(1, 1)
    planted_ok = bool(main["defined"] and negative["defined"] and TOY_ORDER > 2)
    no_further = planted_ok and main["aut_order"] == 2 and main["within_five_percent"]
    negative_triggers = planted_ok and negative["aut_order"] == 4 and not negative["within_five_percent"]
    null_holds = planted_ok and null_within
    matrix_holds = no_further and negative_triggers and null_holds
    return {
        "attack_claimed": False,
        "beyond_matrix": planted_ok and not matrix_holds,
        "experiment_id": EXPERIMENT_ID,
        "main": main,
        "matrix_holds": matrix_holds,
        "negative": negative,
        "null_within_five_percent": null_within,
        "planted_ok": planted_ok,
        "run_id": RUN_ID,
        "toy_order": TOY_ORDER,
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        f"  run_id: {RUN_ID}\n"
        "  attack_claimed: false\n"
        "  metrics:\n"
        f"    planted_ok: {str(result['planted_ok']).lower()}\n"
        f"    matrix_holds: {str(result['matrix_holds']).lower()}\n"
        f"    beyond_matrix: {str(result['beyond_matrix']).lower()}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    write_outputs(Path(args.run_dir), census())


if __name__ == "__main__":
    main()

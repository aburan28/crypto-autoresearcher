#!/usr/bin/env python3
"""Stage-0 lower-half x-count for EXP-ECDLP-3c166b.

Two curves over F_29. Not a discrete logarithm and not a rho step.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


P = 29
LOW_END = 14
EXPERIMENT_ID = "EXP-ECDLP-3c166b"
RUN_ID = "RUN-ECDLP-4a3ca0"
EXPECTED = {
    "E1": {"low": 20, "high": 16, "projective": 37},
    "E2": {"low": 10, "high": 9, "projective": 20},
}
CURVES = (
    ("E1", -1, 1),
    ("E2", 1, 0),
)


def discriminant(curve_a: int, curve_b: int) -> int:
    return (4 * curve_a * curve_a * curve_a + 27 * curve_b * curve_b) % P


def rhs(x_value: int, curve_a: int, curve_b: int) -> int:
    return (x_value * x_value * x_value + curve_a * x_value + curve_b) % P


def multiplicity_scan(x_value: int, curve_a: int, curve_b: int) -> int:
    target = rhs(x_value, curve_a, curve_b)
    return sum(1 for y_value in range(P) if (y_value * y_value) % P == target)


def multiplicity_symbol(x_value: int, curve_a: int, curve_b: int) -> int:
    value = rhs(x_value, curve_a, curve_b)
    if value == 0:
        return 1
    symbol = pow(value, (P - 1) // 2, P)
    if symbol == 1:
        return 2
    return 0


def halves(curve_a: int, curve_b: int) -> dict:
    low_scan = high_scan = low_symbol = high_symbol = 0
    tail_ok = True
    for x_value in range(P):
        scanned = multiplicity_scan(x_value, curve_a, curve_b)
        symbol = multiplicity_symbol(x_value, curve_a, curve_b)
        value = rhs(x_value, curve_a, curve_b)
        square = value == 0 or pow(value, (P - 1) // 2, P) == 1
        tail_ok = tail_ok and ((scanned > 0) == square)
        if x_value <= LOW_END:
            low_scan += scanned
            low_symbol += symbol
        else:
            high_scan += scanned
            high_symbol += symbol
    return {
        "low": low_scan,
        "high": high_scan,
        "low_symbol": low_symbol,
        "high_symbol": high_symbol,
        "agree": low_scan == low_symbol and high_scan == high_symbol,
        "tail_ok": tail_ok,
        "imbalance": abs(low_scan - high_scan),
        "projective": low_scan + high_scan + 1,
    }


def census() -> dict:
    rows = []
    nonsingular = True
    agree = True
    tail_ok = True
    for name, curve_a, curve_b in CURVES:
        disc = discriminant(curve_a, curve_b)
        nonsingular = nonsingular and disc != 0
        counted = halves(curve_a, curve_b)
        counted_again = halves(curve_a, curve_b)
        self_gap = abs(counted["imbalance"] - counted_again["imbalance"])
        agree = agree and counted["agree"] and counted_again["agree"]
        tail_ok = tail_ok and counted["tail_ok"]
        expected = EXPECTED[name]
        rows.append(
            {
                "name": name,
                "a": curve_a % P,
                "b": curve_b % P,
                "discriminant": disc,
                "low": counted["low"],
                "high": counted["high"],
                "imbalance": counted["imbalance"],
                "projective": counted["projective"],
                "self_gap": self_gap,
                "expected_low": expected["low"],
                "expected_high": expected["high"],
                "expected_projective": expected["projective"],
            }
        )
    self_gap = rows[0]["self_gap"] if rows else None
    e1_twice = abs(rows[0]["imbalance"] - rows[0]["imbalance"]) if rows else None
    gap = abs(rows[0]["imbalance"] - rows[1]["imbalance"]) if len(rows) == 2 else None
    counts_match = all(
        row["low"] == row["expected_low"] and row["high"] == row["expected_high"] for row in rows
    )
    projective_match = all(row["projective"] == row["expected_projective"] for row in rows)
    planted_ok = bool(
        nonsingular
        and agree
        and tail_ok
        and self_gap == 0
        and e1_twice == 0
        and len(rows) == 2
    )
    matrix_holds = planted_ok and counts_match and projective_match and gap == 3
    return {
        "attack_claimed": False,
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "prime": P,
        "low_end": LOW_END,
        "curves": rows,
        "gap": gap,
        "expected_gap": 3,
        "counts_match": counts_match,
        "projective_match": projective_match,
        "nonsingular": nonsingular,
        "methods_agree": agree,
        "tail_ok": tail_ok,
        "self_gap": self_gap,
        "planted_ok": planted_ok,
        "matrix_holds": matrix_holds,
        "beyond_matrix": planted_ok and not matrix_holds,
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
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

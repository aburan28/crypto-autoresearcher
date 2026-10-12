#!/usr/bin/env python3
"""Stage-0 transfer-trigger calibration for EXP-SCURVE-7003fe.

TRIGGER is trace 1 or an embedding degree at most 12. The matrix is the
idea's positive-versus-negative reading and is not refit after the counts.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

EXPERIMENT_ID = "EXP-SCURVE-7003fe"
RUN_ID = "RUN-SCURVE-acab50"
EMBEDDING_BOUND = 12
CURVES = (
    {"role": "positive_anomalous", "p": 5, "A": 3, "B": 2},
    {"role": "positive_embedding", "p": 5, "A": 0, "B": 1},
    {"role": "negative", "p": 17, "A": 3, "B": 5},
)


def nonsingular(prime: int, coefficient_a: int, coefficient_b: int) -> bool:
    return (4 * coefficient_a ** 3 + 27 * coefficient_b ** 2) % prime != 0


def count_legendre(prime: int, coefficient_a: int, coefficient_b: int) -> int:
    total = 1
    for x_coord in range(prime):
        residue = (x_coord ** 3 + coefficient_a * x_coord + coefficient_b) % prime
        symbol = pow(residue, (prime - 1) // 2, prime)
        if symbol == 0:
            total += 1
        elif symbol == 1:
            total += 2
    return total


def count_scan(prime: int, coefficient_a: int, coefficient_b: int) -> int:
    total = 1
    squares = {0}
    for y_coord in range(1, prime):
        squares.add(y_coord * y_coord % prime)
    for x_coord in range(prime):
        residue = (x_coord ** 3 + coefficient_a * x_coord + coefficient_b) % prime
        if residue in squares:
            total += 1 if residue == 0 else 2
    return total


def embedding_degree(order: int, prime: int) -> int | None:
    if order <= 1 or order % prime == 0:
        return None
    for degree in range(1, EMBEDDING_BOUND + 1):
        if pow(prime, degree, order) == 1:
            return degree
    return None


def triggers(trace: int, order: int, prime: int) -> bool:
    if trace == 1:
        return True
    return embedding_degree(order, prime) is not None


def curve_row(spec: dict) -> dict:
    prime = spec["p"]
    coefficient_a = spec["A"]
    coefficient_b = spec["B"]
    by_legendre = count_legendre(prime, coefficient_a, coefficient_b)
    by_scan = count_scan(prime, coefficient_a, coefficient_b)
    trace = prime + 1 - by_legendre
    limit = 2 * math.isqrt(prime)
    return {
        "A": coefficient_a,
        "B": coefficient_b,
        "counts_agree": by_legendre == by_scan,
        "hasse": abs(trace) <= limit,
        "nonsingular": nonsingular(prime, coefficient_a, coefficient_b),
        "order": by_legendre,
        "p": prime,
        "role": spec["role"],
        "trace": trace,
        "triggers": triggers(trace, by_legendre, prime),
    }


def census() -> dict:
    rows = [curve_row(spec) for spec in CURVES]
    planted_ok = all(row["counts_agree"] and row["hasse"] and row["nonsingular"] for row in rows)
    by_role = {row["role"]: row["triggers"] for row in rows}
    null_triggers = triggers(0, 5, 5)
    matrix_holds = (
        by_role["positive_anomalous"]
        and by_role["positive_embedding"]
        and not by_role["negative"]
        and not null_triggers
    )
    return {
        "attack_claimed": False,
        "beyond_matrix": planted_ok and not matrix_holds,
        "embedding_bound": EMBEDDING_BOUND,
        "experiment_id": EXPERIMENT_ID,
        "matrix_holds": planted_ok and matrix_holds,
        "null": {"order": 5, "p": 5, "trace": 0, "triggers": null_triggers},
        "planted_ok": planted_ok,
        "rows": rows,
        "run_id": RUN_ID,
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

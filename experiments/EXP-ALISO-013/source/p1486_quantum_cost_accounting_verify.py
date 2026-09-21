#!/usr/bin/env python3
"""Exact exponent audit for the P1486 aggregate quantum claw."""

from __future__ import annotations

import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "research" / "p1486_quantum_cost_accounting_contract_20260729.md"
OUTPUT = (
    ROOT
    / "experiments"
    / "ecdlp_isogeny"
    / "p1486_quantum_cost_accounting_verify_result.json"
)


def frac(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def query_exponent(n: Fraction, r: Fraction) -> Fraction:
    return max(r, n - r / 2)


def generic_gate_exponent(n: Fraction, r: Fraction) -> Fraction:
    return max(n + r / 2, n - r / 2)


def generalized_exponent(
    n: Fraction, r: Fraction, alpha: Fraction
) -> Fraction:
    setup = (1 + alpha) * r
    updates = n + (alpha - Fraction(1, 2)) * r
    endpoint_evaluations = n - r / 2
    return max(setup, updates, endpoint_evaluations)


def rational_grid(limit: Fraction, denominator: int) -> list[Fraction]:
    return [
        Fraction(i, denominator)
        for i in range(int(limit * denominator) + 1)
    ]


def main() -> None:
    started = time.monotonic()
    n = Fraction(1, 3)
    r_query = 2 * n / 3
    registered = {
        "domain": frac(n),
        "query_optimal_r": frac(r_query),
        "query": frac(query_exponent(n, r_query)),
        "gates": frac(generic_gate_exponent(n, r_query)),
        "depth": frac(n - r_query / 2),
        "width": frac(r_query),
        "depth_times_width": frac(n + r_query / 2),
    }
    expected = {
        "domain": "1/3",
        "query_optimal_r": "2/9",
        "query": "2/9",
        "gates": "4/9",
        "depth": "2/9",
        "width": "2/9",
        "depth_times_width": "4/9",
    }
    identity_checks = {
        key: registered[key] == expected[key] for key in expected
    }

    grid = rational_grid(2 * n / 3, 216)
    query_values = [(query_exponent(n, r), r) for r in grid]
    gate_values = [(generic_gate_exponent(n, r), r) for r in grid]
    query_min = min(value for value, _ in query_values)
    gate_min = min(value for value, _ in gate_values)
    query_minimizers = [r for value, r in query_values if value == query_min]
    gate_minimizers = [r for value, r in gate_values if value == gate_min]

    si_n = Fraction(1, 4)
    si_r = 2 * si_n / 3
    sike_control = {
        "domain": frac(si_n),
        "query_optimal_r": frac(si_r),
        "query": frac(query_exponent(si_n, si_r)),
        "gates": frac(generic_gate_exponent(si_n, si_r)),
        "pass": (
            query_exponent(si_n, si_r) == Fraction(1, 6)
            and generic_gate_exponent(si_n, si_r) == Fraction(1, 3)
        ),
    }

    alpha_values = [
        Fraction(0),
        Fraction(1, 16),
        Fraction(1, 8),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(3, 4),
        Fraction(1),
    ]
    alpha_rows = []
    for alpha in alpha_values:
        charged_values = [
            (generalized_exponent(n, r, alpha), r) for r in grid
        ]
        charged = min(value for value, _ in charged_values)
        minimizers = [
            r for value, r in charged_values if value == charged
        ]
        predicted_classical_improvement = alpha < Fraction(1, 2)
        observed_classical_improvement = charged < n
        predicted_quantum_improvement = alpha < Fraction(1, 8)
        observed_quantum_improvement = charged < Fraction(1, 4)
        alpha_rows.append(
            {
                "alpha": frac(alpha),
                "optimized_charged_exponent": frac(charged),
                "minimizers": [frac(r) for r in minimizers],
                "predicted_below_classical_one_third": (
                    predicted_classical_improvement
                ),
                "observed_below_classical_one_third": (
                    observed_classical_improvement
                ),
                "predicted_below_quantum_one_quarter": (
                    predicted_quantum_improvement
                ),
                "observed_below_quantum_one_quarter": (
                    observed_quantum_improvement
                ),
                "pass": (
                    predicted_classical_improvement
                    == observed_classical_improvement
                    and predicted_quantum_improvement
                    == observed_quantum_improvement
                ),
            }
        )

    bjs_width = r_query
    bjs_equal_width = {
        "width": frac(bjs_width),
        "depth": frac(Fraction(1, 4) - bjs_width / 2),
        "gates_and_depth_times_width": frac(
            Fraction(1, 4) + bjs_width / 2
        ),
    }
    ideal_qram = generalized_exponent(n, r_query, Fraction(0))

    mutations = {
        "drop_membership_term": (
            max(r_query, n - r_query / 2)
            != generic_gate_exponent(n, r_query)
        ),
        "sqrt_membership_strictly_improves": not (
            generalized_exponent(n, r_query, Fraction(1, 2)) < n
        ),
        "wrong_query_optimum_left": (
            query_exponent(n, r_query - Fraction(1, 216)) > query_min
        ),
        "wrong_query_optimum_right": (
            query_exponent(n, r_query + Fraction(1, 216)) > query_min
        ),
        "generic_gate_optimum_not_query_optimum": (
            generic_gate_exponent(n, Fraction(0))
            < generic_gate_exponent(n, r_query)
        ),
        "query_count_is_not_standard_gate_breakthrough": (
            query_exponent(n, r_query) < Fraction(1, 4)
            and generic_gate_exponent(n, r_query) > Fraction(1, 4)
        ),
        "alpha_one_eighth_is_not_strict_quantum_improvement": not (
            generalized_exponent(
                n, r_query, Fraction(1, 8)
            )
            < Fraction(1, 4)
        ),
        "ideal_qram_does_beat_serial_bjs_work": (
            ideal_qram < Fraction(1, 4)
        ),
        "equal_width_comparison_is_a_tradeoff": (
            ideal_qram
            < Fraction(1, 4) + bjs_width / 2
            and n - r_query / 2
            > Fraction(1, 4) - bjs_width / 2
        ),
    }

    scientific = {
        "schema": "p1486-quantum-cost-accounting-v2",
        "registered": registered,
        "identity_checks": identity_checks,
        "grid": {
            "denominator": 216,
            "query_min": frac(query_min),
            "query_minimizers": [frac(r) for r in query_minimizers],
            "gate_min": frac(gate_min),
            "gate_minimizers": [frac(r) for r in gate_minimizers],
        },
        "sike_positive_control": sike_control,
        "membership_threshold": alpha_rows,
        "quantum_frontier": {
            "biasse_jao_sankar_serial_time": "1/4",
            "equal_width_parallel_control": bjs_equal_width,
            "ideal_qram_charged_work": frac(ideal_qram),
            "strict_membership_threshold": "alpha < 1/8",
        },
        "mutations": mutations,
    }
    scientific_blob = json.dumps(
        scientific, sort_keys=True, separators=(",", ":")
    ).encode()
    all_pass = (
        all(identity_checks.values())
        and query_min == Fraction(2, 9)
        and query_minimizers == [Fraction(2, 9)]
        and gate_min == Fraction(1, 3)
        and gate_minimizers == [Fraction(0)]
        and sike_control["pass"]
        and all(row["pass"] for row in alpha_rows)
        and bjs_equal_width["depth"] == "5/36"
        and bjs_equal_width["gates_and_depth_times_width"] == "13/36"
        and all(mutations.values())
    )
    result = {
        **scientific,
        "all_pass": all_pass,
        "scientific_data_sha256": hashlib.sha256(scientific_blob).hexdigest(),
        "artifact_hashes": {
            "contract_sha256": sha256(CONTRACT),
            "source_sha256": sha256(Path(__file__)),
        },
        "runtime": {
            "wall_time_sec": time.monotonic() - started,
            "arithmetic": "fractions.Fraction exact rational",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

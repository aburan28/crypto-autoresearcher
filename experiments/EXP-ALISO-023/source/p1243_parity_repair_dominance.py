#!/usr/bin/env python3
"""Verify that divisor selection dominates the parity-repair candidate."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE / "p1243_parity_repaired_kani_probe_result.json"
OUTPUT = HERE / "p1243_parity_repair_dominance_result.json"
CONTRACT = (
    HERE.parent.parent
    / "research"
    / "p1243_parity_repair_dominance_contract_20260729.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def factor(n: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            n //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def sum_two_squares(n: int) -> bool:
    return all(
        prime % 4 != 3 or exponent % 2 == 0
        for prime, exponent in factor(n).items()
    )


def root_count_odd(n: int) -> int:
    if n == 1:
        return 1
    return 1 << len(factor(n))


def largest_prime(n: int) -> int:
    return max(factor(n), default=1)


def scientific_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


def main() -> None:
    source = json.loads(INPUT.read_text())
    rows = []
    all_pass = True
    mutation_gates = []

    for family in source["families"]:
        m = int(family["m"])
        c = int(family["c3_repair"])
        d = int(family["d"])
        n1 = int(family["n1"])
        delta_r = abs(int(family["delta_R"]))
        m0 = m // c
        ell = int(family["L"])

        source_difference = m0 * ell
        repaired_difference = int(family["kani_difference"])
        source_size = n1 * n1 * m0 > 4 * d
        repaired_size = n1 * n1 * m > 4 * c * d
        source_output_multiplier = m0
        repaired_output_multiplier = m * c

        gates = {
            "repair_divides_modulus": m == c * m0,
            "source_divisor_is_odd": m0 % 2 == 1,
            "source_divisor_is_sum_two_squares": sum_two_squares(m0),
            "source_divisor_divides_discriminant": delta_r % m0 == 0,
            "source_divisor_coprime_to_degree": math.gcd(m0, d) == 1,
            "same_L": ell == n1 * n1 * m0 - d,
            "source_difference_sum_two_squares": sum_two_squares(
                source_difference
            ),
            "difference_square_factor_identity": (
                repaired_difference == c * c * source_difference
            ),
            "size_gates_equivalent": source_size == repaired_size,
            "size_gate_passes": source_size,
            "source_root_count_no_larger": (
                root_count_odd(m0) <= root_count_odd(m)
            ),
            "source_largest_prime_no_larger": (
                largest_prime(m0) <= largest_prime(m)
            ),
            "source_output_multiplier_no_larger": (
                source_output_multiplier <= repaired_output_multiplier
            ),
        }
        row_pass = all(gates.values())
        all_pass = all_pass and row_pass

        wrong_m0 = m0 + 1
        mutation = {
            "wrong_divisor_rejected": m != c * wrong_m0,
            "missing_repair_rejected": all(
                item["is_sum_two_squares"] is False
                for item in family["missing_repair_mutations"]
            )
            if family["missing_repair_mutations"]
            else True,
            "difference_increment_rejected": (
                repaired_difference + 1 != c * c * source_difference
            ),
        }
        mutation_gates.append(all(mutation.values()))

        rows.append(
            {
                "name": family["name"],
                "m": m,
                "c": c,
                "m0": m0,
                "d": d,
                "n1": n1,
                "L": ell,
                "source_difference": source_difference,
                "repaired_difference": repaired_difference,
                "source_root_count": root_count_odd(m0),
                "repaired_root_count": root_count_odd(m),
                "source_largest_prime": largest_prime(m0),
                "repaired_largest_prime": largest_prime(m),
                "source_output_multiplier": source_output_multiplier,
                "repaired_output_multiplier": repaired_output_multiplier,
                "gates": gates,
                "mutations": mutation,
                "pass": row_pass,
            }
        )

    all_pass = all_pass and all(mutation_gates)
    scientific = {
        "claim_status": (
            "RESTRICTED DOMINATION THEOREM / EXACT ARITHMETIC CHECK / "
            "NEGATIVE RESULT FOR PARITY-REPAIR COMPLEXITY"
        ),
        "rows": rows,
        "all_pass": all_pass,
        "conclusion": (
            "The source dimension-four construction on m0=m/c has the same "
            "smooth threshold and no larger charged parameters."
        ),
    }
    result = {
        "schema": "p1243-parity-repair-dominance-v1",
        **scientific,
        "artifact_hashes": {
            "input_sha256": sha256(INPUT),
            "contract_sha256": sha256(CONTRACT),
            "source_sha256": sha256(Path(__file__).resolve()),
        },
        "scientific_data_sha256": scientific_hash(scientific),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

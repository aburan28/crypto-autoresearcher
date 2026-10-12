#!/usr/bin/env python3
"""Stage-0 three-slot smoothness census for EXP-PAIR-f4584a.

The accept/reject pattern is the idea's pre-registered reading. It is not
fitted after the values are known.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPERIMENT_ID = "EXP-PAIR-f4584a"
RUN_ID = "RUN-PAIR-e887a4"
BOUND = 7
PRIMES = (2, 3, 5, 7)
POINTS = ((1, 4), (2, 8))
CONTROL_POINT = (4, 4)


def monomial_f(a: int, b: int) -> int:
    return a * a * a + a * b * b + b * b * b


def horner_f(a: int, b: int) -> int:
    return a * (a * a + b * b) + b * b * b


def monomial_g(a: int, b: int) -> int:
    return a * a * a + a * a * b + b * b * b


def horner_g(a: int, b: int) -> int:
    return a * a * (a + b) + b * b * b


def monomial_cube2(a: int, b: int) -> int:
    return a * a * a + 2 * b * b * b


def horner_cube2(a: int, b: int) -> int:
    return (a * a) * a + (b * b) * (2 * b)


def monomial_shift(a: int, b: int) -> int:
    total = a + b
    return total * total * total


def horner_shift(a: int, b: int) -> int:
    total = a + b
    return total * (total * total)


def smooth(value: int) -> bool:
    magnitude = abs(value)
    if magnitude == 0:
        return False
    for prime in PRIMES:
        while magnitude % prime == 0:
            magnitude //= prime
    return magnitude == 1


def accepts(first: int, second: int, third: int) -> bool:
    return sum(1 for value in (first, second, third) if smooth(value)) >= 2


def paired(a: int, b: int) -> dict:
    values = {
        "f": [monomial_f(a, b), horner_f(a, b)],
        "g": [monomial_g(a, b), horner_g(a, b)],
        "x^3+2": [monomial_cube2(a, b), horner_cube2(a, b)],
        "(x+1)^3": [monomial_shift(a, b), horner_shift(a, b)],
    }
    agreed = all(pair[0] == pair[1] for pair in values.values())
    settled = {name: pair[0] for name, pair in values.items()}
    return {
        "a": a,
        "agreed": agreed,
        "b": b,
        "duplicate_accepts": accepts(settled["f"], settled["g"], settled["f"]),
        "nearby_accepts": accepts(settled["f"], settled["g"], settled["(x+1)^3"]),
        "pair_accepts": smooth(settled["f"]) and smooth(settled["g"]),
        "treatment_accepts": accepts(settled["f"], settled["g"], settled["x^3+2"]),
        "values": values,
    }


def census() -> dict:
    named = [paired(*point) for point in POINTS]
    control = paired(*CONTROL_POINT)
    agreed = all(cell["agreed"] for cell in named) and control["agreed"]
    nearby_ok = all(cell["nearby_accepts"] for cell in named)
    pair_rejects = all(not cell["pair_accepts"] for cell in named)
    control_ok = (
        control["duplicate_accepts"]
        and control["treatment_accepts"]
        and control["nearby_accepts"]
    )
    zero_rejected = not smooth(0)
    planted_ok = agreed and nearby_ok and pair_rejects and control_ok and zero_rejected
    duplicate = [cell["duplicate_accepts"] for cell in named]
    treatment = [cell["treatment_accepts"] for cell in named]
    gap_holds = duplicate == [True, True] and treatment == [False, False]
    return {
        "attack_claimed": False,
        "beyond_pattern": planted_ok and not gap_holds,
        "bound": BOUND,
        "control_point": {"a": CONTROL_POINT[0], "b": CONTROL_POINT[1]},
        "experiment_id": EXPERIMENT_ID,
        "gap_holds": planted_ok and gap_holds,
        "named_points": named,
        "planted_ok": planted_ok,
        "run_id": RUN_ID,
        "zero_is_not_smooth": zero_rejected,
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
        f"    gap_holds: {str(result['gap_holds']).lower()}\n"
        f"    beyond_pattern: {str(result['beyond_pattern']).lower()}\n",
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

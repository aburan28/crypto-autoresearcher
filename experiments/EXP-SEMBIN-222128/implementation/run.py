#!/usr/bin/env python3
"""Stage-0 HKYY closure for one unsatisfiable toy ideal and one satisfiable toy ideal.

The unsatisfiable generators are x, y, and xy+1 over GF(2). The satisfiable
generators are x+1 and y+1. V_{F,D} is the GF(2) span of the generators,
closed under multiplication by x or y whenever the product has degree <= D.
D_ref is the least D in 0..4 whose closure contains the constant 1.
D_pin is the least such D whose closure contains both x+1 and y+1.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "crypto.autoresearch.exp-sembin-222128.stage0.v1"
HYPOTHESIS = "H-SEMBIN-f17c97"
EXPERIMENT = "EXP-SEMBIN-222128"
NVARS = 2
D_MAX = 4


def _monomials(degree_cap: int) -> list[tuple[int, int]]:
    return [(x_exp, y_exp)
            for total in range(degree_cap + 1)
            for x_exp in range(total + 1)
            if (y_exp := total - x_exp) >= 0]


def _mask(exponents: dict[tuple[int, int], int], index: dict[tuple[int, int], int]) -> int:
    mask = 0
    for monomial, present in exponents.items():
        if present and monomial in index:
            mask |= 1 << index[monomial]
    return mask


def _lift(mask: int, variable: int, monomials: list[tuple[int, int]], index: dict[tuple[int, int], int]) -> int:
    lifted = 0
    for position, (x_exp, y_exp) in enumerate(monomials):
        if mask & (1 << position):
            moved = (x_exp + 1, y_exp) if variable == 0 else (x_exp, y_exp + 1)
            if moved not in index:
                return 0
            lifted |= 1 << index[moved]
    return lifted


def _insert(mask: int, pivots: dict[int, int]) -> bool:
    while mask:
        bit = mask & -mask
        position = bit.bit_length() - 1
        if position in pivots:
            mask ^= pivots[position]
            continue
        for old in list(pivots):
            if pivots[old] & bit:
                pivots[old] ^= mask
        pivots[position] = mask
        return True
    return False


def _in_span(mask: int, pivots: dict[int, int]) -> bool:
    current = mask
    while current:
        bit = current & -current
        position = bit.bit_length() - 1
        if position not in pivots:
            return False
        current ^= pivots[position]
    return True


def closure(generators: list[dict[tuple[int, int], int]], degree_cap: int) -> dict[int, int]:
    monomials = _monomials(degree_cap)
    index = {monomial: position for position, monomial in enumerate(monomials)}
    pivots: dict[int, int] = {}
    for generator in generators:
        if generator and max(sum(monomial) for monomial in generator) <= degree_cap:
            _insert(_mask(generator, index), pivots)
    grew = True
    while grew:
        grew = False
        for mask in list(pivots.values()):
            for variable in range(NVARS):
                if _insert(_lift(mask, variable, monomials, index), pivots):
                    grew = True
    return pivots


def contains(target: dict[tuple[int, int], int], pivots: dict[int, int], degree_cap: int) -> bool:
    index = {monomial: position for position, monomial in enumerate(_monomials(degree_cap))}
    return _in_span(_mask(target, index), pivots)


def least_degree(generators: list[dict[tuple[int, int], int]], target: dict[tuple[int, int], int]) -> int | None:
    for degree_cap in range(0, D_MAX + 1):
        if contains(target, closure(generators, degree_cap), degree_cap):
            return degree_cap
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.stage != "0":
        raise SystemExit("stage 0 only")
    if args.trial_id != "hkyy-toy-closure":
        raise SystemExit("unexpected trial id")
    zero = (0, 0)
    one = {(zero): 1}
    unsat = [
        {(1, 0): 1},
        {(0, 1): 1},
        {(1, 1): 1, zero: 1},
    ]
    sat = [
        {(1, 0): 1, zero: 1},
        {(0, 1): 1, zero: 1},
    ]
    d_ref = least_degree(unsat, one)
    d_pin = least_degree(sat, {(1, 0): 1, zero: 1})
    d_pin_second = least_degree(sat, {(0, 1): 1, zero: 1})
    sat_contains_one = contains(one, closure(sat, D_MAX), D_MAX)
    payload = {
        "schema": SCHEMA,
        "experiment_id": EXPERIMENT,
        "hypothesis_id": HYPOTHESIS,
        "trial_id": args.trial_id,
        "stage": 0,
        "nvars": NVARS,
        "d_max": D_MAX,
        "d_ref": d_ref,
        "d_pin": d_pin,
        "d_pin_second": d_pin_second,
        "sat_contains_one": sat_contains_one,
        "pins_agree": d_pin == d_pin_second,
    }
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_dir / "manifest.yaml").write_text(
        "schema: crypto.autoresearch.run_manifest.v1\n"
        f"experiment_id: {EXPERIMENT}\n"
        f"hypothesis_id: {HYPOTHESIS}\n"
        f"trial_id: {args.trial_id}\n"
        "artifacts:\n"
        "  - raw-result.json\n"
        "  - RESULTS.md\n",
        encoding="utf-8",
    )
    (run_dir / "RESULTS.md").write_text(
        f"# {EXPERIMENT} stage 0\n\n"
        f"d_ref {d_ref}. d_pin {d_pin}. The chain-length slope is not computed.\n",
        encoding="utf-8",
    )
    print(json.dumps({key: payload[key] for key in ("d_ref", "d_pin", "d_pin_second", "sat_contains_one", "pins_agree")}))


if __name__ == "__main__":
    main()

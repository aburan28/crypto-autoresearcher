#!/usr/bin/env python3
"""Statement-only derivation of the five encoded divisor predicates.

Source transcribed from blind-statements.json: an integer's bit i is the
coefficient of X^i over F2. Divide by cancelling the leading bit with shifted
XOR, with at most degree(p)+1 cancellations. Test every monic mask of degree
1 through floor(degree(p)/2).

Run: python3 independent.py > output.json
No producer source, result, or external module is imported.
"""

import json


MASKS = (131081, 313, 471, 131073, 257)
CONTROL_DIVISOR = 3


def degree(mask):
    if mask <= 0:
        raise ValueError("degree needs a positive mask")
    return mask.bit_length() - 1


def remainder(dividend, divisor, fuel=None):
    if dividend < 0 or divisor <= 0:
        raise ValueError("invalid polynomial mask")
    if fuel is None:
        fuel = degree(dividend) + 1 if dividend else 0
    current = dividend
    steps = 0
    while current and degree(current) >= degree(divisor) and steps < fuel:
        current ^= divisor << (degree(current) - degree(divisor))
        steps += 1
    unfinished = bool(current and degree(current) >= degree(divisor))
    return {"remainder": current, "steps": steps, "unfinished": unfinished}


def analyze(mask):
    n = degree(mask)
    per_degree = []
    first_zero = None
    candidate_count = 0
    zero_count = 0
    maximum_steps = 0
    candidate_rows = []
    zero_divisors = []
    for j in range(1, n // 2 + 1):
        degree_zero_count = 0
        for lower in range(1 << j):
            divisor = (1 << j) | lower
            result = remainder(mask, divisor)
            assert not result["unfinished"], (mask, divisor, result)
            candidate_count += 1
            maximum_steps = max(maximum_steps, result["steps"])
            candidate_rows.append({
                "degree": j,
                "lower": lower,
                "divisor": divisor,
                "remainder": result["remainder"],
                "steps": result["steps"],
            })
            if result["remainder"] == 0:
                zero_count += 1
                degree_zero_count += 1
                zero_divisors.append(divisor)
                if first_zero is None:
                    first_zero = {
                        "degree": j,
                        "lower": lower,
                        "divisor": divisor,
                        "steps": result["steps"],
                    }
        per_degree.append({
            "degree": j,
            "candidates": 1 << j,
            "zero_remainders": degree_zero_count,
        })
    assert candidate_count == sum(1 << j for j in range(1, n // 2 + 1))
    return {
        "mask": mask,
        "degree": n,
        "candidate_count": candidate_count,
        "predicate": zero_count == 0,
        "zero_remainder_count": zero_count,
        "zero_divisors": zero_divisors,
        "first_zero": first_zero,
        "maximum_reduction_steps": maximum_steps,
        "per_degree": per_degree,
        "candidate_rows": candidate_rows,
    }


def control(mask):
    exact = remainder(mask, CONTROL_DIVISOR)
    # Independent degree-one check: reduction modulo X+1 equals p(1),
    # the parity of the number of set coefficients.
    parity = bin(mask).count("1") & 1
    assert exact["remainder"] == parity
    assert not exact["unfinished"]
    short = remainder(mask, CONTROL_DIVISOR, fuel=exact["steps"] - 1)
    assert short["unfinished"] and short["remainder"] == 3
    return {
        "mask": mask,
        "divisor": CONTROL_DIVISOR,
        "degree_one_lower_endpoint": 1,
        "remainder": exact["remainder"],
        "parity_at_one": parity,
        "steps": exact["steps"],
        "allowed_fuel": degree(mask) + 1,
        "one_step_short": short,
    }


def main():
    results = [analyze(mask) for mask in MASKS]
    controls = [control(mask) for mask in (131073, 257)]
    for row in results:
        assert row["candidate_count"] == (510 if row["degree"] == 17 else 30)
    assert all(row["first_zero"] == {
        "degree": 1,
        "lower": 1,
        "divisor": 3,
        "steps": degree(row["mask"]),
    } for row in results if row["mask"] in (131073, 257))
    print(json.dumps({
        "schema": "binstd.blind-review-raw.v1",
        "results": results,
        "degree_one_controls": controls,
        "boundary_test": {
            "description": "The last degree-one lower mask is 1, giving divisor 3. "
                           "Each control needs exactly degree(mask) XOR steps; "
                           "one fewer leaves mask 3 as an unfinished remainder.",
            "controls": controls,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

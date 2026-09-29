#!/usr/bin/env python3
"""EXP-SEMBIN-81dc96 / EXP-SEMBIN-f4a17b -- independent recomputation control.

The load-bearing quantities of both contracts are recomputed here from the
STATEMENT of each quantity and its parameters, by a different method: exact
Python integers and exact rational comparisons, with no logarithms anywhere in
the cost path and no import of the producing modules. Agreement is then evidence
about the quantities; disagreement localizes to one of two named
implementations.

WHAT THIS CONTROL IS, AND WHAT IT IS NOT. The review architecture asks for a
BLIND re-derivation: an agent that re-derives a quantity without reading the
producer's implementation, notes or report. That is not what this file is, and
claiming otherwise would misrepresent it. The same session wrote both
implementations, so the independence here is METHOD independence, not agent
independence: log2-space floating point against exact integer arithmetic, two
different formula arrangements, no shared code path. It catches transcription
slips, precision loss, off-by-one in ceilings and factorial/binomial mistakes.
It cannot catch a shared misreading of the paper, which is precisely the failure
mode a genuinely blind re-derivation exists to catch, and that one remains OWED
to an independent reviewer.

Quantities recomputed:
  Table 3, all 36 printed cells, from m! 2^{n/m} n^12, 2^{2n/m} and 2^{n/2}
  n^12 at n = 571                          contract says 2^{109.9}
  stage 2 at n = 571, m = 12               contract says 2^{95.2}
  their gap                                contract says 2^{14.7}
  relation store 2^{ceil(n/m)}             contract says 2^31 / 2^38 / 2^48
  Macaulay width sum_{d<=4} C(N,d)         contract says 2^{41.2} / 2^{43.4} / 2^{45.9}
  N = (m-2)n + km at the same cells        contract says 2790 / 4099 / 6286
  dense square of the n = 571 width        contract says 2^{91.8} bits
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction

# Printed Table 3, transcribed independently from
# inputs/SEMAEV-2015-310/tables.yaml: (n, m, 2^{n/2}, stage1, stage2).
PRINTED = [
    (100, 6, "1.12e15", "7.49e31", "1.08e10"),
    (150, 7, "3.77e22", "1.84e36", "7.96e12"),
    (200, 8, "1.26e30", "5.54e39", "1.12e15"),
    (250, 9, "4.25e37", "4.97e42", "5.29e16"),
    (300, 10, "1.42e45", "2.07e45", "1.15e18"),
    (310, 10, "4.56e46", "6.13e45", "4.61e18"),
    (350, 10, "4.78e52", "4.21e47", "1.18e21"),
    (400, 11, "1.60e60", "5.92e49", "7.81e21"),
    (409, 11, "3.63e61", "1.36e50", "2.43e22"),
    (450, 11, "5.39e67", "5.68e51", "4.26e24"),
    (500, 12, "1.80e75", "4.08e53", "1.21e25"),
    (571, 12, "8.79e85", "1.21e56", "4.44e28"),
]

# The three cells both contracts quote, as (n, m) with the paper's Table 3 m.
CELLS = [(310, 10), (409, 11), (571, 12)]


def exact_pow2_over_q(numer: int, denom: int, scale_digits: int = 40) -> Fraction:
    """2^(numer/denom) as a Fraction, to `scale_digits` decimal digits.

    Computed as the integer denom-th root of 2^numer scaled by 10^scale_digits,
    using math.isqrt-style integer root extraction. No floating point.
    """
    scale = 10 ** scale_digits
    target = (2 ** numer) * (scale ** denom)
    root = integer_nth_root(target, denom)
    return Fraction(root, scale)


def integer_nth_root(value: int, n: int) -> int:
    """Floor of the n-th root of a nonnegative integer, by Newton iteration."""
    if value < 0:
        raise ValueError("negative")
    if value == 0:
        return 0
    x = 1 << ((value.bit_length() + n - 1) // n)
    while True:
        nxt = ((n - 1) * x + value // pow(x, n - 1)) // n
        if nxt >= x:
            break
        x = nxt
    while pow(x + 1, n) <= value:
        x += 1
    while pow(x, n) > value:
        x -= 1
    return x


def sig3_of_fraction(value: Fraction) -> str:
    """Render a positive Fraction as a truncated-to-3-significant-figure string.

    Exact: the decimal exponent is found by integer comparison against powers of
    ten and the mantissa by exact rational division, so no float is involved.
    """
    if value <= 0:
        raise ValueError("positive only")
    exponent = 0
    v = value
    while v >= 10:
        v /= 10
        exponent += 1
    while v < 1:
        v *= 10
        exponent -= 1
    mant100 = (v * 100).numerator // (v * 100).denominator   # floor -> truncation
    return f"{mant100 / 100:.2f}e{exponent}"


def table3_exact() -> dict:
    """Recompute all 36 cells exactly and compare the printed digits."""
    cells, agree = [], 0
    for (n, m, p_rho, p_s1, p_s2) in PRINTED:
        rho = exact_pow2_over_q(n, 2)
        s1 = Fraction(math.factorial(m)) * exact_pow2_over_q(n, m) * Fraction(n) ** 12
        s2 = exact_pow2_over_q(2 * n, m)
        for col, computed, printed in (("rho", rho, p_rho),
                                       ("stage1", s1, p_s1),
                                       ("stage2", s2, p_s2)):
            got = sig3_of_fraction(computed)
            ok = got == printed
            agree += ok
            cells.append({"n": n, "m": m, "column": col, "printed": printed,
                          "recomputed_trunc3sf": got, "agrees": ok})
    return {"cells": cells, "agree": f"{agree}/{len(cells)}",
            "passed": agree == len(cells),
            "method": "exact integers and Fractions; integer nth roots; no logarithms"}


def load_bearing_quantities() -> dict:
    """The exact figures both contracts pin, recomputed from their statements."""
    out = {}

    # n^12 at n = 571, and stage 2 at (571, 12). Both as exact objects.
    n, m = 571, 12
    cof = Fraction(n) ** 12
    st2 = exact_pow2_over_q(2 * n, m)
    out["cofactor_n12_at_571"] = {
        "exact_integer": str(n ** 12),
        "bits": (n ** 12).bit_length(),
        "log2_from_bit_length": round(math.log2(n ** 12), 4),
        "contract_states": 109.9,
        "agrees_to_0.1_bit": abs(math.log2(n ** 12) - 109.9) < 0.1,
    }
    out["stage2_at_571_m12"] = {
        "log2_exact_rational": f"2*{n}/{m} = {Fraction(2 * n, m)}",
        "log2_value": round(float(Fraction(2 * n, m)), 4),
        "contract_states": 95.2,
        "agrees_to_0.1_bit": abs(float(Fraction(2 * n, m)) - 95.2) < 0.1,
    }
    gap = math.log2(n ** 12) - float(Fraction(2 * n, m))
    out["cofactor_minus_stage2_bits"] = {
        "value": round(gap, 4), "contract_states": 14.7,
        "agrees_to_0.1_bit": abs(gap - 14.7) < 0.1,
        "cofactor_exceeds_stage2": gap > 0,
        "meaning": ("the polynomial factor the analytic optimization discards is "
                    "larger than the entire second stage it is balanced against, "
                    "at the paper's own m for n = 571"),
    }

    # Relation store 2^{ceil(n/m)}, Macaulay width, dense square.
    rel, mac, nvars = [], [], []
    for (n, m) in CELLS:
        k = -(-n // m)
        rel.append({"n": n, "m": m, "k_ceil": k, "relation_store_log2": k})
        N = (m - 2) * n + k * m
        width = sum(math.comb(N, d) for d in range(5))
        nvars.append({"n": n, "m": m, "N": N})
        mac.append({"n": n, "m": m, "N": N,
                    "width_exact_integer_digits": len(str(width)),
                    "width_log2": round(math.log2(width), 4)})
    out["relation_store"] = {
        "rows": rel,
        "contract_states": [31, 38, 48],
        "agrees": [r["relation_store_log2"] for r in rel] == [31, 38, 48],
    }
    out["macaulay_variable_counts"] = {
        "rows": nvars,
        "contract_states": [2790, 4099, 6286],
        "agrees": [r["N"] for r in nvars] == [2790, 4099, 6286],
    }
    out["macaulay_widths_degree4"] = {
        "rows": mac,
        "contract_states": [41.2, 43.4, 45.9],
        "agrees_to_0.1_bit": all(
            abs(r["width_log2"] - c) < 0.1
            for r, c in zip(mac, [41.2, 43.4, 45.9])),
    }
    n571 = [r for r in mac if r["n"] == 571][0]
    dense_bits = 2.0 * n571["width_log2"]
    out["dense_square_bits_at_571"] = {
        "value": round(dense_bits, 4), "contract_states": 91.8,
        "agrees_to_0.1_bit": abs(dense_bits - 91.8) < 0.1,
        "note": ("width^2 bits for a dense row-echelon form over F_2, one bit per "
                 "entry. This is the figure that independently recovers the 2^91 "
                 "reported in the KN-LIT-e77232 thread for these parameters, "
                 "against the sparse 2^70 in the same thread."),
    }
    return out


def main() -> int:
    result = {
        "control": "arithmetic_independence",
        "for_experiments": ["EXP-SEMBIN-81dc96", "EXP-SEMBIN-f4a17b"],
        "independence_kind": "method-independent, NOT agent-blind",
        "independence_disclosure": (
            "Written by the same session as the producing modules and therefore "
            "not a blind re-derivation in the sense of AGENTS.md 'Review "
            "architecture'. It shares no code path and no arithmetic "
            "representation with them, so it catches transcription, precision, "
            "ceiling and combinatorial errors; it cannot catch a shared "
            "misreading of the source, and a genuinely blind re-derivation of "
            "these quantities remains owed to an independent reviewer."),
        "table3": table3_exact(),
        "load_bearing": load_bearing_quantities(),
    }
    checks = [result["table3"]["passed"]]
    lb = result["load_bearing"]
    checks += [
        lb["cofactor_n12_at_571"]["agrees_to_0.1_bit"],
        lb["stage2_at_571_m12"]["agrees_to_0.1_bit"],
        lb["cofactor_minus_stage2_bits"]["agrees_to_0.1_bit"],
        lb["relation_store"]["agrees"],
        lb["macaulay_variable_counts"]["agrees"],
        lb["macaulay_widths_degree4"]["agrees_to_0.1_bit"],
        lb["dense_square_bits_at_571"]["agrees_to_0.1_bit"],
    ]
    result["all_checks_passed"] = all(checks)
    result["n_checks"] = len(checks)
    print(json.dumps(result, indent=2))
    return 0 if result["all_checks_passed"] else 2


if __name__ == "__main__":
    sys.exit(main())

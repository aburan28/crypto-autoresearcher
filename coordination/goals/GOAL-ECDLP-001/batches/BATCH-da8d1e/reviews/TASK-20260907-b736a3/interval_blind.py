#!/usr/bin/env python3
"""Blind re-derivation of interval-partition q_maj and q_strict.

Implements the quantity stated in
coordination/goals/GOAL-ECDLP-001/batches/BATCH-da8d1e/review_plan.yaml
(blind_rederivation.quantity) at n=23, s=3. Enumerates every pair in
{0,...,n-1}^2. Uses exact rationals (fractions.Fraction). Does not import
or read any producer implementation.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

N_PARAM = 23
S_PARAM = 3
EXPECTED_Q_MAJ = Fraction(284, 529)
EXPECTED_Q_STRICT = Fraction(0, 1)


def v(k: int, n: int = N_PARAM, s: int = S_PARAM) -> int:
    """Interval partition label: min(floor(k*s/n), s-1)."""
    return min((k * s) // n, s - 1)


def enumerate_interval(n: int = N_PARAM, s: int = S_PARAM) -> dict:
    pair_count = n * n
    fibers: dict[int, list[int]] = {a: [] for a in range(s)}
    v_of: list[int] = []
    for k in range(n):
        label = v(k, n, s)
        v_of.append(label)
        fibers[label].append(k)

    # N[a,b,c] = #{(k,ell) : v(k)=a, v(ell)=b, v((k+ell) mod n)=c}
    counts: dict[tuple[int, int, int], int] = defaultdict(int)
    enumerated = 0
    for k in range(n):
        a = v_of[k]
        for ell in range(n):
            b = v_of[ell]
            c = v_of[(k + ell) % n]
            counts[(a, b, c)] += 1
            enumerated += 1

    if enumerated != pair_count:
        raise RuntimeError(f"enumeration size {enumerated} != n^2={pair_count}")

    n_table: dict[str, int] = {}
    max_per_ab: dict[str, int] = {}
    support_per_ab: dict[str, list[int]] = {}
    maj_sum = 0
    strict_pairs = 0
    ab_strict: dict[str, bool] = {}

    for a in range(s):
        for b in range(s):
            row = [int(counts[(a, b, c)]) for c in range(s)]
            for c, val in enumerate(row):
                n_table[f"{a},{b},{c}"] = val
            support = [c for c, val in enumerate(row) if val > 0]
            support_per_ab[f"{a},{b}"] = support
            row_max = max(row) if row else 0
            max_per_ab[f"{a},{b}"] = row_max
            maj_sum += row_max
            forced = len(support) == 1
            ab_strict[f"{a},{b}"] = forced
            if forced:
                strict_pairs += sum(row)

    q_maj = Fraction(maj_sum, pair_count)
    q_strict = Fraction(strict_pairs, pair_count)

    if sum(n_table.values()) != pair_count:
        raise RuntimeError("N[a,b,c] does not partition the pair set")

    return {
        "n": n,
        "s": s,
        "pair_count": pair_count,
        "v": v_of,
        "fibers": {str(a): fibers[a] for a in range(s)},
        "fiber_sizes": {str(a): len(fibers[a]) for a in range(s)},
        "N": n_table,
        "max_c_N_ab": max_per_ab,
        "support_c_ab": support_per_ab,
        "ab_strict": ab_strict,
        "maj_numerator": maj_sum,
        "strict_numerator": strict_pairs,
        "q_maj": f"{q_maj.numerator}/{q_maj.denominator}",
        "q_strict": f"{q_strict.numerator}/{q_strict.denominator}",
        "q_maj_expected": f"{EXPECTED_Q_MAJ.numerator}/{EXPECTED_Q_MAJ.denominator}",
        "q_strict_expected": f"{EXPECTED_Q_STRICT.numerator}/{EXPECTED_Q_STRICT.denominator}",
        "q_maj_holds": q_maj == EXPECTED_Q_MAJ,
        "q_strict_holds": q_strict == EXPECTED_Q_STRICT,
        "holds": q_maj == EXPECTED_Q_MAJ and q_strict == EXPECTED_Q_STRICT,
    }


def main() -> int:
    result = enumerate_interval()
    out_path = Path(__file__).with_name("blind_raw.json")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out_path.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["holds"] else 1


if __name__ == "__main__":
    sys.exit(main())

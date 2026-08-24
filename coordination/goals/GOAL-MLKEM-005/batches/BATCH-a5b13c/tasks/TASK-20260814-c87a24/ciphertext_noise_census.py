#!/usr/bin/env python3
"""Stage A -- the exact Compress_d fibre census over Z_q, q = 3329.

TASK-20260814-c87a24 (GOAL-MLKEM-005 / BATCH-a5b13c), executing PREREG-7
section 2 exactly. Pure Python integer/exact-rational arithmetic. No
external dependency (stdlib only: fractions, math, json, collections).

FIPS 203 DEFINITION (verified against the primary source, section 4.2.1,
"Compression and decompression", and the rounding-operator definition in
section 2.3 -- see ciphertext_noise_writeup.md for the exact citation and
why the committed inputs/MLKEM-DUAL-SOURCES-20260802 corpus did not itself
carry this passage):

    Compress_d : Z_q -> Z_{2^d},   x |-> round((2^d / q) * x) mod 2^d
    Decompress_d : Z_{2^d} -> Z_q, y |-> round((q / 2^d) * y)

    round(v): "the rounding of v to the nearest integer. If v = y + 1/2 for
    some y in Z, then round(v) = y + 1" -- i.e. ROUND-HALF-UP (ties broken
    upward, not round-half-to-even and not round-half-away-from-zero in
    general). On this script's domain every argument to round() is
    non-negative (x in [0, q-1], 2^d/q * x >= 0), so round-half-up and
    round-half-away-from-zero coincide here; the distinction is stated
    explicitly because it would matter off this domain.

    FIPS 203 states explicitly: "Division and rounding in the computation
    of these functions are performed in the set of rational numbers.
    Floating-point computations shall not be used." This script honours
    that literally: every intermediate value is a `fractions.Fraction`,
    never a `float`.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from fractions import Fraction

Q = 3329


def round_half_up(v: Fraction) -> int:
    """FIPS 203's round(): nearest integer, ties broken UP. Exact rational
    arithmetic throughout -- `math.floor` on a `Fraction` is exact."""
    return math.floor(v + Fraction(1, 2))


def compress(x: int, d: int, q: int = Q) -> int:
    assert 0 <= x < q
    return round_half_up(Fraction(x * (1 << d), q)) % (1 << d)


def decompress(y: int, d: int, q: int = Q) -> int:
    assert 0 <= y < (1 << d)
    return round_half_up(Fraction(y * q, 1 << d))


def centered_delta(x: int, rt: int, q: int = Q) -> int:
    """The signed residue of (x - rt) mod q, in (-q/2, q/2] -- the
    representative that actually matters for an LWE-style equation over
    Z_q, since Compress/Decompress arithmetic is circular mod q. A naive
    integer subtraction x - rt (without centering) produces a spurious huge
    outlier for residues near the q-1/0 wraparound boundary (verified
    empirically: exactly one residue at d=10 has raw x-rt = 3328 instead of
    the true signed distance -1, which would silently inflate any variance
    computed from the uncentered value by several orders of magnitude).
    Used by ciphertext_noise_readout.py's Stage B noise-variance
    computation; Stage A's own census (fibre histograms, roundtrip-equality
    counts, the d=12 gate) never uses delta's magnitude or sign, only
    x == rt, so this correction does not change any Stage A number."""
    raw = x - rt
    return ((raw + q // 2) % q) - q // 2


def census_for_d(d: int, q: int = Q) -> dict:
    """Build the fibre structure for Compress_d over all q residues."""
    fibres = defaultdict(list)
    for x in range(q):
        fibres[compress(x, d, q)].append(x)
    sizes = Counter(len(v) for v in fibres.values())
    result = {
        "d": d,
        "num_codewords_2pow_d": 1 << d,
        "num_residues_q": q,
        "num_fibres_populated": len(fibres),
        "fibre_size_histogram": dict(sorted(sizes.items())),
        "sum_check_sizes_times_counts": sum(s * c for s, c in sizes.items()),
    }
    return result, fibres


def roundtrip_agreement(d: int, q: int = Q) -> dict:
    exact = 0
    mismatches_in_singleton_fibres = 0
    _, fibres = census_for_d(d, q)
    singleton_residues = {v[0] for v in fibres.values() if len(v) == 1}
    for x in range(q):
        y = compress(x, d, q)
        rt = decompress(y, d, q)
        if rt == x:
            exact += 1
        elif x in singleton_residues:
            mismatches_in_singleton_fibres += 1
    return {
        "d": d,
        "exact_roundtrip_matches": exact,
        "total_residues": q,
        "singleton_fibre_count": len(singleton_residues),
        "mismatches_among_singleton_residues": mismatches_in_singleton_fibres,
    }


def mutual_information_delta_bin_d12(q: int = Q) -> dict:
    """d = 12: 2^12 = 4096 > q = 3329, so every fibre is forced to be a
    singleton (an injective map cannot have a repeated codeword on a domain
    smaller than its codomain -- but we do not assume this, we CHECK it by
    the actual census below). Because every fibre is a singleton,
    Decompress_12(Compress_12(x)) = x for every x, so
    delta(x) = x - Decompress_12(Compress_12(x)) is IDENTICALLY ZERO -- a
    constant random variable under any distribution on x (including the
    stated simple model, x uniform on Z_q). A constant carries zero
    information about any other variable, so I(delta; bin) = 0 exactly, a
    fact forced by the census itself (every fibre singleton -> delta is the
    zero constant), not computed via a separate Monte Carlo estimate of a
    quantity the census already determines exactly."""
    d = 12
    stats, fibres = census_for_d(d, q)
    all_singleton = all(len(v) == 1 for v in fibres.values())
    deltas = []
    for x in range(q):
        y = compress(x, d, q)
        rt = decompress(y, d, q)
        deltas.append(x - rt)
    delta_is_constant_zero = all(delta == 0 for delta in deltas)
    # I(delta;bin) under x ~ Uniform(Z_q): if delta is the constant 0,
    # H(delta) = 0 bits, hence I(delta;bin) = H(delta) - H(delta|bin) = 0 - 0 = 0
    # exactly, regardless of H(delta|bin) (both terms individually 0 here).
    i_delta_bin = 0.0 if delta_is_constant_zero else None
    return {
        "d": d,
        "every_fibre_singleton": all_singleton,
        "delta_identically_zero": delta_is_constant_zero,
        "I_delta_bin_under_uniform_x_model": i_delta_bin,
        "note": (
            "delta is a constant (0) whenever every fibre is a singleton, so "
            "I(delta;bin)=0 is forced by the census itself, not estimated."
        ),
    }


def falsification_check(census_d10, census_d11, gate_d12) -> dict:
    """F(a): singleton count at d_u=11 must be exactly 767 (1281 doublets);
    d_u=10 census must be exactly 767 fibres of size 3 and 257 of size 4.
    F(d): the d=12 gate must return every fibre a singleton with
    I(delta;bin)=0 exactly."""
    hist11 = census_d11["fibre_size_histogram"]
    hist10 = census_d10["fibre_size_histogram"]
    f_a_d11_ok = hist11.get("1") == 767 and hist11.get("2") == 1281 and len(hist11) == 2
    f_a_d10_ok = hist10.get("3") == 767 and hist10.get("4") == 257 and len(hist10) == 2
    f_a = f_a_d11_ok and f_a_d10_ok
    f_d = bool(gate_d12["every_fibre_singleton"]) and gate_d12["I_delta_bin_under_uniform_x_model"] == 0.0
    return {
        "F_a_singleton_count_d11_is_767_and_doublets_1281": f_a_d11_ok,
        "F_a_d10_census_matches_767x3_257x4": f_a_d10_ok,
        "F_a_overall_clears": f_a,
        "F_d_d12_gate_clears": f_d,
        "stage_A_complete_and_stands_independently": f_a and f_d,
    }


def stringify_hist(hist: dict) -> dict:
    return {str(k): v for k, v in hist.items()}


def run_full_census() -> dict:
    d_values = [4, 5, 10, 11, 12]
    per_d = {}
    for d in d_values:
        stats, _fibres = census_for_d(d)
        stats["fibre_size_histogram"] = stringify_hist(stats["fibre_size_histogram"])
        per_d[str(d)] = stats

    rt11 = roundtrip_agreement(11)
    gate12 = mutual_information_delta_bin_d12()

    census_d10 = {k: (v if k != "fibre_size_histogram" else {kk: vv for kk, vv in v.items()})
                  for k, v in per_d["10"].items()}
    census_d11 = per_d["11"]

    falsification = falsification_check(census_d10, census_d11, gate12)

    return {
        "q": Q,
        "rounding_convention": {
            "fips203_specifies": "round-half-up (ties broken upward: v=y+1/2 => round(v)=y+1)",
            "this_implementation_uses": "round-half-up via exact Fraction arithmetic "
                                          "(math.floor(v + Fraction(1,2))); coincides with "
                                          "round-half-away-from-zero on this script's "
                                          "non-negative-argument domain",
            "floating_point_used": False,
        },
        "per_d_fibre_census": per_d,
        "d11_roundtrip_agreement": rt11,
        "d12_mutual_information_gate": gate12,
        "falsification": falsification,
    }


def main() -> int:
    result = run_full_census()
    print(json.dumps(result, indent=2, sort_keys=False))
    fal = result["falsification"]
    print("\n--- STAGE A SUMMARY ---", file=sys.stderr)
    print(f"F(a) clears: {fal['F_a_overall_clears']}", file=sys.stderr)
    print(f"F(d) clears: {fal['F_d_d12_gate_clears']}", file=sys.stderr)
    print(f"Stage A complete and stands independently: "
          f"{fal['stage_A_complete_and_stands_independently']}", file=sys.stderr)
    return 0 if (fal["F_a_overall_clears"] and fal["F_d_d12_gate_clears"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())

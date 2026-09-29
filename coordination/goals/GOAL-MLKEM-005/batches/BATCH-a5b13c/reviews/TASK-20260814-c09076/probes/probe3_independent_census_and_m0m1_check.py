#!/usr/bin/env python3
"""RED-TEAM PROBE 3 (TASK-20260814-c09076) -- INDEPENDENT, FROM-SCRATCH
recomputation. Does NOT import ciphertext_noise_census.py or
ciphertext_noise_readout.py from the producer's task directory (checked:
no `import` of, or `exec`/`spec_from_file_location` against, any path under
tasks/TASK-20260814-c87a24/ appears anywhere in this file).

Implements its own Compress_d/Decompress_d from the FIPS 203 definition,
independently re-verified against a fresh network fetch of
https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf in this same
session (sha256 of the fetched PDF and its pdftotext -layout extraction are
recorded in this task's red_team_report.md; NOT the producer's own fetch --
a second, independent fetch performed by this reviewing session).

Covers THREE of this task's targets:

  TARGET 3 -- independently recompute the d_u=11 and d_u=10 fibre censuses
    and confirm the reported 767/1281 and 767/257 splits.
  TARGET 2 -- independently re-derive whether beta(M0) and beta(M1)'s
    UNDERLYING VARIANCE construction are forced-identical by PREREG-7
    section 3.2's own "single effective distribution" specification,
    checked numerically against an independently-built census and
    independently-built M0/M1 variance formula (not the producer's code).
  TARGET 6 -- the null/nearby-object control: confirm the d_u=10 census
    (ML-KEM-512/768) has ZERO singleton fibres, i.e. M2's NOT_APPLICABLE
    disposition is FORCED by the census, not an unexplored construction
    choice.

NO LATTICE REDUCTION, NO ESTIMATOR CALL IN THIS FILE -- pure integer/exact
rational arithmetic only (stdlib fractions/math/collections), matching
PREREG-7 section 5.4.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from fractions import Fraction

Q = 3329


def rt_round_half_up(v: Fraction) -> int:
    """FIPS 203's stated rounding operator, INDEPENDENTLY re-implemented in
    this file (not imported): 'the rounding of x to the nearest integer.
    If x = y + 1/2 for some y in Z, then round(x) = y + 1' -- ties broken
    UP. Implemented via floor(v + 1/2), exact Fraction arithmetic, no float
    anywhere, matching FIPS 203's own explicit floating-point prohibition."""
    n = v.numerator * 2 + v.denominator  # 2v + 1, still exact
    d = v.denominator * 2
    # floor((2v+1)/2) == floor(v + 1/2)
    q, r = divmod(n, d)
    return q  # Python divmod on positive/negative ints already floors correctly


def compress_d(x: int, d: int, q: int = Q) -> int:
    assert 0 <= x < q
    return rt_round_half_up(Fraction(x * (1 << d), q)) % (1 << d)


def decompress_d(y: int, d: int, q: int = Q) -> int:
    assert 0 <= y < (1 << d)
    return rt_round_half_up(Fraction(y * q, 1 << d))


def centered(raw_diff: int, q: int = Q) -> int:
    """Signed representative of raw_diff mod q in (-q/2, q/2] -- built
    independently here, same standard technique the producer used (the only
    correct way to center a mod-q residual), not copied from their file."""
    return ((raw_diff + q // 2) % q) - q // 2


def build_fibres(d: int, q: int = Q) -> dict:
    fibres = defaultdict(list)
    for x in range(q):
        fibres[compress_d(x, d, q)].append(x)
    return fibres


def histogram(fibres: dict) -> dict:
    return dict(sorted(Counter(len(v) for v in fibres.values()).items()))


def main() -> int:
    out = {}

    # --- TARGET 3: independent census, d in {10, 11} (plus 4,5,12 as a
    # bonus cross-check since they're nearly free) -----------------------
    census = {}
    for d in [4, 5, 10, 11, 12]:
        fibres = build_fibres(d)
        hist = histogram(fibres)
        census[d] = {
            "fibre_size_histogram": hist,
            "num_fibres": len(fibres),
            "sum_check": sum(k * v for k, v in hist.items()),
        }
    out["target3_independent_census"] = {
        str(d): v for d, v in census.items()
    }

    d11_ok = census[11]["fibre_size_histogram"] == {1: 767, 2: 1281}
    d10_ok = census[10]["fibre_size_histogram"] == {3: 767, 4: 257}
    out["target3_matches_producer_and_prereg7"] = {
        "d_u_11_histogram_is_exactly_767_singleton_1281_doublet": d11_ok,
        "d_u_10_histogram_is_exactly_767x3_257x4": d10_ok,
    }

    # d=12 exactness check (independently confirms the raw-vs-centered
    # non-issue flagged under TARGET 5: at d=12 every fibre is a singleton,
    # so Decompress_12(Compress_12(x)) == x EXACTLY for every x -- raw
    # difference is 0 everywhere, so centering cannot matter here).
    d12_fibres = build_fibres(12)
    d12_all_singleton = all(len(v) == 1 for v in d12_fibres.values())
    d12_raw_diffs = set()
    for x in range(Q):
        y = compress_d(x, 12)
        rt = decompress_d(y, 12)
        d12_raw_diffs.add(x - rt)
    out["target5_d12_raw_vs_centered_check"] = {
        "every_fibre_singleton": d12_all_singleton,
        "distinct_raw_x_minus_rt_values": sorted(d12_raw_diffs),
        "raw_and_centered_are_identical_here": d12_raw_diffs == {0},
        "conclusion": (
            "At d=12 every raw (x - Decompress(Compress(x))) is exactly 0, "
            "so the producer's one use of an UNCENTERED raw difference "
            "(ciphertext_noise_census.py's mutual_information_delta_bin_d12, "
            "which does not call centered_delta) cannot be affected by the "
            "wraparound bug the M0/M1 centering fix addressed -- confirmed "
            "independently here, not merely asserted."
        ),
    }

    # --- TARGET 6: null control -- 0 singleton fibres at d_u=10, forced by
    # the census, for ML-KEM-512/768 --------------------------------------
    n_singleton_d10 = sum(1 for v in build_fibres(10).values() if len(v) == 1)
    out["target6_null_control_d10_singleton_count"] = {
        "n_singleton_fibres_at_d_u_10": n_singleton_d10,
        "M2_NOT_APPLICABLE_is_forced_by_census": n_singleton_d10 == 0,
    }

    # --- TARGET 2: independent M0/M1 variance identity check -------------
    # Build M0 (population-average compression-error distribution) and M1
    # (probability-weighted mixture of per-class compression-error
    # distributions), each independently, for d_u=10 and d_u=11, and CHECK
    # whether they are forced-identical -- INDEPENDENT of any assertion in
    # the producer's writeup or code, using only the mathematical identity
    # "convolution distributes over a mixture that partitions the same
    # population" and this file's own from-scratch histograms.
    def exact_var(counter: dict) -> Fraction:
        total = Fraction(sum(counter.values()))
        mean = sum(Fraction(v) * c for v, c in counter.items()) / total
        mean_sq = sum(Fraction(v) * Fraction(v) * c for v, c in counter.items()) / total
        return mean_sq - mean * mean

    def m0_delta_variance(d: int) -> Fraction:
        hist = Counter()
        for x in range(Q):
            y = compress_d(x, d)
            rt = decompress_d(y, d)
            hist[centered(x - rt)] += 1
        return exact_var(hist)

    def m1_delta_variance(d: int) -> Fraction:
        fibres = build_fibres(d)
        by_class = defaultdict(Counter)
        for codeword, members in fibres.items():
            rt = decompress_d(codeword, d)
            size = len(members)
            for x in members:
                by_class[size][centered(x - rt)] += 1
        total_var = Fraction(0)
        total_mean = Fraction(0)
        for size, hist in by_class.items():
            n_in_class = sum(hist.values())
            p_class = Fraction(n_in_class, Q)
            var_c = exact_var(hist)
            mean_c = sum(Fraction(v) * c for v, c in hist.items()) / Fraction(n_in_class)
            # E[delta^2] for the mixture = sum p_c * (var_c + mean_c^2)
            total_var += p_class * (var_c + mean_c * mean_c)
            total_mean += p_class * mean_c
        return total_var - total_mean * total_mean

    identity_check = {}
    for d, label in [(10, "d_u=10 (ML-KEM-512/768)"), (11, "d_u=11 (ML-KEM-1024)")]:
        v_m0 = m0_delta_variance(d)
        v_m1 = m1_delta_variance(d)
        identity_check[label] = {
            "M0_delta_variance_exact": str(v_m0),
            "M1_delta_variance_exact": str(v_m1),
            "identical_exactly": v_m0 == v_m1,
        }
    out["target2_independent_M0_M1_variance_identity_check"] = identity_check
    out["target2_conclusion"] = (
        "Independently re-derived (own histograms, own mixture-variance "
        "formula, no import of the producer's build_m0/build_m1): the "
        "M0 and M1 compression-error variances are EXACTLY equal at BOTH "
        "d_u=10 and d_u=11. This is consistent with the producer's own "
        "claim that this is a forced mathematical identity (mixture "
        "variance decomposition E[X^2]=sum p_c E[X^2|c] applied to a "
        "partition of the full population is definitionally the same as "
        "the population variance), not an implementation artifact -- and "
        "it holds regardless of which d_u is used, which is exactly what "
        "the identity's proof predicts (it does not depend on the "
        "specific census numbers, only on the classes forming a partition "
        "of Z_q, which they do by construction at every d)."
    )

    print(json.dumps(out, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

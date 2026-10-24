#!/usr/bin/env python3
"""Blind re-derivation for TASK-20261022-8ebef8 (EXP-CZLIFT-1a3453), joint J3.

Written from experiments/EXP-CZLIFT-1a3453/specification.yaml,
experiments/EXP-CZLIFT-1a3453/trial-plan.json and
ledger/hypotheses/H-CZLIFT-fba874.yaml only, plus general mathematics.  No
producer implementation, raw result, or decision was read before this file and
its output were sealed (sha256 recorded in blind/SEALED.sha256).

Statement used (hypothesis H-CZLIFT-fba874, spec objective/metrics):
  * digit function f(k), k = 1..m with m = n_half = (n-1)/2 (n odd prime);
  * psi_a(x) = exp(2 pi i a x / p), a = 1..p-1 (all nontrivial additive
    characters of F_p); chi_t(k) = exp(+-2 pi i t k / n), t = 0..n-1 (FFT over
    Z/n, all n characters);
  * statistic X(a,t) = |sum_{k=1}^{m} psi_a(f(k)) chi_t(k)|^2 / m;
  * per digit: max_power = max_{a,t} X(a,t); spikes = #{(a,t): X > T};
  * T(p,n) = ln((p-1) n) + 12  (spec objective; hypothesis statement);
  * null: X(a,t) ~ Exp(1) per pair (hypothesis assumptions).

Quantities derived:
  (A) threshold T(p,n) and the family-wise level it implies per digit and per
      experiment for the stated numbers of characters, digits and curves;
  (B) a simulation check of the Exp(1) null and of the null maximum on the
      half range with uniform digits (the uniform control's distribution);
  (C) the half-range statistic on the planted PTM-1 sequence
      f(k) = floor(p k / n) mod p, for every prime p in [50, 600] and every
      odd prime n in [11, p + 1 + 2 sqrt(p)], n != p (a superset of the
      family the spec describes), with the trivial-bound blind zone
      m <= T(p,n) in which no sequence whatsoever can register a spike.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

MARGIN = 12.0
SEEDS = [20261009, 20261010]          # spec replication.seeds
N_CM_MAX = 24                         # spec inputs.cm_arm "first 24"
RANDOM_PRIMES = [53, 71, 101, 131, 173, 211, 263, 307, 367, 421, 487, 557]
N_COORDS = 2                          # x, y
DIGITS = [0, 1, 2, 3, 4]              # precision 5
HIGHER = [1, 2, 3, 4]


def primes_upto(x: int) -> list[int]:
    s = bytearray([1]) * (x + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(x ** 0.5) + 1):
        if s[i]:
            s[i * i :: i] = bytearray(len(s[i * i :: i]))
    return [i for i in range(x + 1) if s[i]]


def threshold(p: int, n: int) -> float:
    return math.log((p - 1) * n) + MARGIN


def spectrum(digits: np.ndarray, p: int, n: int) -> np.ndarray:
    """X(a,t) for a = 1..p-1 (rows) and t = 0..n-1 (cols).

    digits[j] is f(k) for k = j+1, j = 0..m-1.  The sequence is placed at
    positions k = 1..m of a length-n array and transformed; the sign
    convention of chi_t is irrelevant because the max/count runs over all t.
    """
    m = (n - 1) // 2
    assert digits.shape == (m,)
    a = np.arange(1, p, dtype=np.int64)[:, None]
    phase = (a * digits[None, :].astype(np.int64)) % p
    z = np.zeros((p - 1, n), dtype=np.complex128)
    z[:, 1 : m + 1] = np.exp(2j * np.pi * phase / p)
    S = np.fft.fft(z, axis=1)
    return (S.real ** 2 + S.imag ** 2) / m


def direct_X(digits, p, n, a, t):
    m = (n - 1) // 2
    s = 0j
    for k in range(1, m + 1):
        s += complex(math.cos(2 * math.pi * (a * digits[k - 1] / p - t * k / n)),
                     math.sin(2 * math.pi * (a * digits[k - 1] / p - t * k / n)))
    return abs(s) ** 2 / m


def planted(p: int, n: int) -> np.ndarray:
    m = (n - 1) // 2
    k = np.arange(1, m + 1, dtype=np.int64)
    return (p * k // n) % p


def part_A() -> dict:
    e12 = math.exp(-MARGIN)
    n_curves = N_CM_MAX + len(RANDOM_PRIMES)
    fam_higher = n_curves * N_COORDS * len(HIGHER)
    fam_all = n_curves * N_COORDS * len(DIGITS)
    out = {
        "threshold_formula": "T(p,n) = ln((p-1)*n) + 12",
        "pairs_per_digit_N": "(p-1)*n  (p-1 nontrivial psi x n characters of Z/n)",
        "per_digit_bonferroni_level": e12,
        "per_digit_level_distinct_values": e12 / 2,
        "note_conjugate_pairs": (
            "X(a,t) = X(p-a, n-t) exactly (complex conjugate sums), a != p-a for odd p, "
            "so every spike count is even and only (p-1)n/2 values are distinct; "
            "Bonferroni over distinct values gives e^-12/2 per digit."),
        "max_curves_per_seed": n_curves,
        "families_per_seed": {
            "higher_digit_real": fam_higher,
            "digit0_real": n_curves * N_COORDS,
            "shuffled_all_digits": fam_all,
            "uniform_all_digits": fam_all,
        },
        "fwer_bonferroni_per_seed": {
            "spikes_higher_digits_gt0": fam_higher * e12,
            "shuffled_spikes_total_gt0": fam_all * e12,
            "uniform_spikes_total_gt0": fam_all * e12,
        },
        "fwer_success_criterion_fails_under_null_two_seeds_bonferroni":
            len(SEEDS) * (fam_higher + 2 * fam_all) * e12,
        "fwer_success_criterion_fails_under_null_two_seeds_distinct":
            len(SEEDS) * (fam_higher + 2 * fam_all) * e12 / 2,
        "margin_for_experiment_wide_level_e^-12":
            "ln(N) + 12 + ln(#families) = ln(N) + 12 + ln(%d) = ln(N) + %.3f (one seed, real+controls)"
            % (fam_higher + 2 * fam_all, 12 + math.log(fam_higher + 2 * fam_all)),
        "falsification_requires_two_seeds": True,
        "range_of_T_over_stated_family": {
            "min_example_p53_n11": threshold(53, 11),
            "max_example_p599_n641": threshold(599, 641),
        },
    }
    return out


def part_B(rng_seed: int = 20261022) -> dict:
    rng = np.random.default_rng(rng_seed)
    configs = [(53, 13), (53, 59), (131, 127), (263, 271), (421, 419), (557, 563), (599, 593)]
    draws = 60
    res = []
    for p, n in configs:
        m = (n - 1) // 2
        T = threshold(p, n)
        maxima = []
        tail = {5: 0, 10: 0}
        total = 0
        for _ in range(draws):
            d = rng.integers(0, p, size=m)
            X = spectrum(d, p, n)
            maxima.append(float(X.max()))
            total += X.size
            for x in tail:
                tail[x] += int((X > x).sum())
        N = (p - 1) * n
        res.append({
            "p": p, "n": n, "m": m, "T": T, "draws": draws,
            "null_max_mean": float(np.mean(maxima)),
            "null_max_sd": float(np.std(maxima)),
            "null_max_max": float(np.max(maxima)),
            "draws_with_max_above_T": int(sum(v > T for v in maxima)),
            "ln_N_over_2_plus_euler_gamma": math.log(N / 2) + 0.5772156649,
            "marginal_tail_P_X_gt_5": tail[5] / total, "exp_minus_5": math.exp(-5),
            "marginal_tail_P_X_gt_10": tail[10] / total, "exp_minus_10": math.exp(-10),
            "trivial_bound_m": m,
        })
    return {"rng": "numpy.random.default_rng(%d)" % rng_seed, "configs": res}


def part_C() -> dict:
    ps = [q for q in primes_upto(600) if q >= 50]
    rows = {}
    # spot-check FFT against the direct sum on a few cells
    checks = []
    for p, n in [(53, 47), (101, 97), (307, 311)]:
        d = planted(p, n)
        X = spectrum(d, p, n)
        a, t = np.unravel_index(int(X.argmax()), X.shape)
        checks.append({"p": p, "n": n, "fft": float(X[a, t]),
                       "direct": direct_X(d, p, n, int(a) + 1, int(t))})
    for p in ps:
        hi = int(p + 1 + 2 * math.isqrt(p) + 2)
        for n in primes_upto(hi):
            if n < 11 or n == p or n % 2 == 0:
                continue
            if n > p + 1 + 2 * math.sqrt(p):
                continue
            m = (n - 1) // 2
            T = threshold(p, n)
            X = spectrum(planted(p, n), p, n)
            mx = float(X.max())
            a, t = np.unravel_index(int(X.argmax()), X.shape)
            rows["%d,%d" % (p, n)] = {
                "m": m, "T": round(T, 6), "planted_max": round(mx, 6),
                "argmax_a": int(a) + 1, "argmax_t": int(t),
                "planted_spikes": int((X > T).sum()),
                "excess": round(mx - T, 6),
                "blind_zone_m_le_T": bool(m <= T),
            }
    # smallest n escaping the trivial-bound blind zone, per p
    nmin = {}
    for p in ps:
        n = 11
        while not ((n - 1) / 2 > threshold(p, n)):
            n += 2
        nmin[str(p)] = n
    return {"direct_sum_checks": checks, "grid": rows,
            "smallest_odd_n_with_m_gt_T_by_p": nmin}


def main(out_path: str) -> None:
    A = part_A()
    B = part_B()
    C = part_C()
    g = C["grid"]
    vals = list(g.values())
    summary = {
        "grid_cells": len(vals),
        "cells_in_blind_zone": sum(v["blind_zone_m_le_T"] for v in vals),
        "cells_planted_spike": sum(v["planted_spikes"] > 0 for v in vals),
        "cells_outside_blind_zone_without_spike":
            [k for k, v in g.items() if not v["blind_zone_m_le_T"] and v["planted_spikes"] == 0],
        "min_ratio_planted_max_over_m": min(v["planted_max"] / v["m"] for v in vals),
        "max_ratio_planted_max_over_m": max(v["planted_max"] / v["m"] for v in vals),
    }
    out = {"A_threshold_and_level": A, "B_null_calibration": B,
           "C_planted_PTM1": C, "C_summary": summary}
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({"A": A, "B": B, "C_checks": C["direct_sum_checks"],
                      "C_summary": summary,
                      "nmin_examples": {k: C["smallest_odd_n_with_m_gt_T_by_p"][k]
                                        for k in ["53", "101", "307", "557", "599"]}},
                     indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
